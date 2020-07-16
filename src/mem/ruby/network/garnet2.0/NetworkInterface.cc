/*
 * Copyright (c) 2008 Princeton University
 * Copyright (c) 2016 Georgia Institute of Technology
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met: redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer;
 * redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution;
 * neither the name of the copyright holders nor the names of its
 * contributors may be used to endorse or promote products derived from
 * this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * Authors: Niket Agarwal
 *          Tushar Krishna
 */


#include "mem/ruby/network/garnet2.0/NetworkInterface.hh"

#include <cassert>
#include <cmath>

#include "base/cast.hh"
#include "base/stl_helpers.hh"
#include "debug/RubyNetwork.hh"
#include "mem/ruby/network/MessageBuffer.hh"
#include "mem/ruby/network/garnet2.0/Credit.hh"
#include "mem/ruby/network/garnet2.0/flitBuffer.hh"
#include "mem/ruby/slicc_interface/Message.hh"

using namespace std;
using m5::stl_helpers::deletePointers;

NetworkInterface::NetworkInterface(const Params *p)
    : ClockedObject(p), Consumer(this), m_id(p->id),
      m_virtual_networks(p->virt_nets), m_vc_per_vnet(p->vcs_per_vnet),
      m_num_vcs(m_vc_per_vnet * m_virtual_networks),
      m_deadlock_threshold(p->garnet_deadlock_threshold),
      vc_busy_counter(m_virtual_networks, 0)


{
    m_router_id = -1;
    m_vc_round_robin = 0;
    m_ni_out_vcs.resize(m_num_vcs);
    m_ni_out_vcs_enqueue_time.resize(m_num_vcs);
    outCreditQueue = new flitBuffer();

    // instantiating the NI flit buffers
    for (int i = 0; i < m_num_vcs; i++) {
        m_ni_out_vcs[i] = new flitBuffer();
        m_ni_out_vcs_enqueue_time[i] = Cycles(INFINITE_);
    }

    m_vc_allocator.resize(m_virtual_networks); // 1 allocator per vnet
    for (int i = 0; i < m_virtual_networks; i++) {
        m_vc_allocator[i] = 0;
    }

    m_stall_count.resize(m_virtual_networks);
}

void
NetworkInterface::init()
{
    for (int i = 0; i < m_num_vcs; i++) {
        m_out_vc_state.push_back(new OutVcState(i, m_net_ptr));
    }
}

NetworkInterface::~NetworkInterface()
{
    deletePointers(m_out_vc_state);
    deletePointers(m_ni_out_vcs);
    delete outCreditQueue;
    delete outFlitQueue;
}

void
NetworkInterface::addInPort(NetworkLink *in_link,
                              CreditLink *credit_link)
{
    inNetLink = in_link;
    in_link->setLinkConsumer(this);
    outCreditLink = credit_link;
    credit_link->setSourceQueue(outCreditQueue);
}

void
NetworkInterface::addOutPort(NetworkLink *out_link,
                             CreditLink *credit_link,
                             SwitchID router_id)
{
    inCreditLink = credit_link;
    credit_link->setLinkConsumer(this);

    outNetLink = out_link;
    outFlitQueue = new flitBuffer();
    out_link->setSourceQueue(outFlitQueue);

    m_router_id = router_id;
}

void
NetworkInterface::addNode(vector<MessageBuffer *>& in,
                            vector<MessageBuffer *>& out)
{
    inNode_ptr = in;
    outNode_ptr = out;

    for (auto& it : in) {
        if (it != nullptr) {
            it->setConsumer(this);
        }
    }
}

void
NetworkInterface::dequeueCallback()
{
    // An output MessageBuffer has dequeued something this cycle and there
    // is now space to enqueue a stalled message. However, we cannot wake
    // on the same cycle as the dequeue. Schedule a wake at the soonest
    // possible time (next cycle).
    scheduleEventAbsolute(clockEdge(Cycles(1)));
}

void
NetworkInterface::incrementStats(flit *t_flit)
{
    int vnet = t_flit->get_vnet();

    // Latency
    m_net_ptr->increment_received_flits(vnet);
    Cycles network_delay =
        t_flit->get_dequeue_time() - t_flit->get_enqueue_time() - Cycles(1);
    Cycles src_queueing_delay = t_flit->get_src_delay();
    Cycles dest_queueing_delay = (curCycle() - t_flit->get_dequeue_time());
    Cycles queueing_delay = src_queueing_delay + dest_queueing_delay;

    m_net_ptr->increment_flit_network_latency(network_delay, vnet);
    m_net_ptr->increment_flit_queueing_latency(queueing_delay, vnet);

    if (t_flit->get_type() == TAIL_ || t_flit->get_type() == HEAD_TAIL_) {
        m_net_ptr->increment_received_packets(vnet);
        m_net_ptr->increment_packet_network_latency(network_delay, vnet);
        m_net_ptr->increment_packet_queueing_latency(queueing_delay, vnet);
    }

    // Hops
    m_net_ptr->increment_total_hops(t_flit->get_route().hops_traversed);
}

/*
 * The NI wakeup checks whether there are any ready messages in the protocol
 * buffer. If yes, it picks that up, flitisizes it into a number of flits and
 * puts it into an output buffer and schedules the output link. On a wakeup
 * it also checks whether there are flits in the input link. If yes, it picks
 * them up and if the flit is a tail, the NI inserts the corresponding message
 * into the protocol buffer. It also checks for credits being sent by the
 * downstream router.
 */

void
NetworkInterface::wakeup()
{
    DPRINTF(RubyNetwork, "Network Interface %d connected to router %d "
            "woke up at time: %lld\n", m_id, m_router_id, curCycle());

    MsgPtr msg_ptr;
    Tick curTime = clockEdge();

    // Checking for messages coming from the protocol
    // can pick up a message/cycle for each virtual net
    if (!m_net_ptr->isTaskGraphEnabled()){
        for (int vnet = 0; vnet < inNode_ptr.size(); ++vnet) {
            MessageBuffer *b = inNode_ptr[vnet];
            if (b == nullptr) {
                continue;
            }

            if (b->isReady(curTime)) { // Is there a message waiting
                msg_ptr = b->peekMsgPtr();
                if (flitisizeMessage(msg_ptr, vnet)) {
                    b->dequeue(curTime);
                }
            }
        }
    } else {
        task_execution();
        updateGeneratorBuffer();
    }

    scheduleOutputLink();
    checkReschedule();

    // Check if there are flits stalling a virtual channel. Track if a
    // message is enqueued to restrict ejection to one message per cycle.
    bool messageEnqueuedThisCycle = checkStallQueue();

    /*********** Check the incoming flit link **********/
    if (inNetLink->isReady(curCycle())) {
        flit *t_flit = inNetLink->consumeLink();
        int vnet = t_flit->get_vnet();
        t_flit->set_dequeue_time(curCycle());

        if (!m_net_ptr->isTaskGraphEnabled()){
        // If a tail flit is received, enqueue into the protocol buffers if
        // space is available. Otherwise, exchange non-tail flits for credits.
            if (t_flit->get_type() == TAIL_ || t_flit->get_type() \
            == HEAD_TAIL_) {
                if (!messageEnqueuedThisCycle &&
                outNode_ptr[vnet]->areNSlotsAvailable(1, curTime)) {
                // Space is available. Enqueue to protocol buffer.
                outNode_ptr[vnet]->enqueue(t_flit->get_msg_ptr(), curTime,
                                            cyclesToTicks(Cycles(1)));

                // Simply send a credit back since we are not buffering
                // this flit in the NI
                sendCredit(t_flit, true);

                // Update stats and delete flit pointer
                incrementStats(t_flit);
                delete t_flit;
                } else {
                // No space available- Place tail flit in stall queue and set
                // up a callback for when protocol buffer is dequeued. Stat
                // update and flit pointer deletion will occur upon unstall.
                m_stall_queue.push_back(t_flit);
                m_stall_count[vnet]++;

                auto cb = std::bind(&NetworkInterface::dequeueCallback, this);
                outNode_ptr[vnet]->registerDequeueCallback(cb);
                }
            } else {
                // Non-tail flit. Send back a credit but not VC free signal.
                sendCredit(t_flit, false);

                // Update stats and delete flit pointer.
                incrementStats(t_flit);
                delete t_flit;
            }
        } else {

            //task graph
            int temp_src = t_flit->get_tg_info().src_task;
            int temp_edge_id = t_flit->get_tg_info().edge_id;
            int temp_task = t_flit->get_tg_info().dest_task;

            GraphTask &dest_task = get_task_by_task_id(temp_task);
            GraphEdge &dest_edge = dest_task.\
                get_incoming_edge_by_eid(temp_edge_id);

            assert(dest_edge.get_src_task_id() == temp_src);
            //

            if (t_flit->get_type() == TAIL_ || t_flit->get_type() == \
            HEAD_TAIL_) {
                //received a pkt
                dest_edge.record_pkt(t_flit);
                /*
                DPRINTF(TaskGraph, " NI %d received the tail flit \
                from the NI %d \n", m_id, t_flit->get_route().src_ni);
                */

                sendCredit(t_flit, true);

                // Update stats and delete flit pointer
                incrementStats(t_flit);
                delete t_flit;
            } else {
                sendCredit(t_flit, false);

                // Update stats and delete flit pointer.
                incrementStats(t_flit);
                delete t_flit;

            }

        }
    }

    /****************** Check the incoming credit link *******/

    if (inCreditLink->isReady(curCycle())) {
        Credit *t_credit = (Credit*) inCreditLink->consumeLink();
        m_out_vc_state[t_credit->get_vc()]->increment_credit();
        if (t_credit->is_free_signal()) {
            m_out_vc_state[t_credit->get_vc()]->setState(IDLE_, curCycle());
        }
        delete t_credit;
    }


    // It is possible to enqueue multiple outgoing credit flits if a message
    // was unstalled in the same cycle as a new message arrives. In this
    // case, we should schedule another wakeup to ensure the credit is sent
    // back.
    if (outCreditQueue->getSize() > 0) {
        outCreditLink->scheduleEventAbsolute(clockEdge(Cycles(1)));
    }
}

void
NetworkInterface::sendCredit(flit *t_flit, bool is_free)
{
    Credit *credit_flit = new Credit(t_flit->get_vc(), is_free, curCycle());
    outCreditQueue->insert(credit_flit);
}

bool
NetworkInterface::checkStallQueue()
{
    bool messageEnqueuedThisCycle = false;
    Tick curTime = clockEdge();

    if (!m_stall_queue.empty()) {
        for (auto stallIter = m_stall_queue.begin();
             stallIter != m_stall_queue.end(); ) {
            flit *stallFlit = *stallIter;
            int vnet = stallFlit->get_vnet();

            // If we can now eject to the protocol buffer, send back credits
            if (outNode_ptr[vnet]->areNSlotsAvailable(1, curTime)) {
                outNode_ptr[vnet]->enqueue(stallFlit->get_msg_ptr(), curTime,
                                           cyclesToTicks(Cycles(1)));

                // Send back a credit with free signal now that the VC is no
                // longer stalled.
                sendCredit(stallFlit, true);

                // Update Stats
                incrementStats(stallFlit);

                // Flit can now safely be deleted and removed from stall queue
                delete stallFlit;
                m_stall_queue.erase(stallIter);
                m_stall_count[vnet]--;

                // If there are no more stalled messages for this vnet, the
                // callback on it's MessageBuffer is not needed.
                if (m_stall_count[vnet] == 0)
                    outNode_ptr[vnet]->unregisterDequeueCallback();

                messageEnqueuedThisCycle = true;
                break;
            } else {
                ++stallIter;
            }
        }
    }

    return messageEnqueuedThisCycle;
}

// Embed the protocol message into flits
bool
NetworkInterface::flitisizeMessage(MsgPtr msg_ptr, int vnet)
{
    Message *net_msg_ptr = msg_ptr.get();
    NetDest net_msg_dest = net_msg_ptr->getDestination();

    // gets all the destinations associated with this message.
    vector<NodeID> dest_nodes = net_msg_dest.getAllDest();

    // Number of flits is dependent on the link bandwidth available.
    // This is expressed in terms of bytes/cycle or the flit size
    int num_flits = (int) ceil((double) m_net_ptr->MessageSizeType_to_int(
        net_msg_ptr->getMessageSize())/m_net_ptr->getNiFlitSize());

    // loop to convert all multicast messages into unicast messages
    for (int ctr = 0; ctr < dest_nodes.size(); ctr++) {

        // this will return a free output virtual channel
        int vc = calculateVC(vnet);

        if (vc == -1) {
            return false ;
        }
        MsgPtr new_msg_ptr = msg_ptr->clone();
        NodeID destID = dest_nodes[ctr];

        Message *new_net_msg_ptr = new_msg_ptr.get();
        if (dest_nodes.size() > 1) {
            NetDest personal_dest;
            for (int m = 0; m < (int) MachineType_NUM; m++) {
                if ((destID >= MachineType_base_number((MachineType) m)) &&
                    destID < MachineType_base_number((MachineType) (m+1))) {
                    // calculating the NetDest associated with this destID
                    personal_dest.clear();
                    //next to add is MachineID constructor
                    personal_dest.add((MachineID) {(MachineType) m, (destID -
                        MachineType_base_number((MachineType) m))});
                    new_net_msg_ptr->getDestination() = personal_dest;
                    break;
                }
            }
            net_msg_dest.removeNetDest(personal_dest);
            // removing the destination from the original message to reflect
            // that a message with this particular destination has been
            // flitisized and an output vc is acquired
            net_msg_ptr->getDestination().removeNetDest(personal_dest);
        }

        // Embed Route into the flits
        // NetDest format is used by the routing table
        // Custom routing algorithms just need destID
        RouteInfo route;
        route.vnet = vnet;
        route.net_dest = new_net_msg_ptr->getDestination();
        route.src_ni = m_id;
        route.src_router = m_router_id;
        route.dest_ni = destID;
        route.dest_router = m_net_ptr->get_router_id(destID);
        route.vc_chioce = (route.dest_router >= route.src_router);

        // initialize hops_traversed to -1
        // so that the first router increments it to 0
        route.hops_traversed = -1;

        m_net_ptr->increment_injected_packets(vnet);
        for (int i = 0; i < num_flits; i++) {
            m_net_ptr->increment_injected_flits(vnet);
            flit *fl = new flit(i, vc, vnet, route, num_flits, new_msg_ptr,
                curCycle());

            fl->set_src_delay(curCycle() - ticksToCycles(msg_ptr->getTime()));
            m_ni_out_vcs[vc]->insert(fl);
        }

        m_ni_out_vcs_enqueue_time[vc] = curCycle();
        m_out_vc_state[vc]->setState(ACTIVE_, curCycle());
    }
    return true ;
}

// Looking for a free output vc
int
NetworkInterface::calculateVC(int vnet)
{
    for (int i = 0; i < m_vc_per_vnet; i++) {
        int delta = m_vc_allocator[vnet];
        m_vc_allocator[vnet]++;
        if (m_vc_allocator[vnet] == m_vc_per_vnet)
            m_vc_allocator[vnet] = 0;

        if (m_out_vc_state[(vnet*m_vc_per_vnet) + delta]->isInState(
                    IDLE_, curCycle())) {
            vc_busy_counter[vnet] = 0;
            return ((vnet*m_vc_per_vnet) + delta);
        }
    }

    vc_busy_counter[vnet] += 1;
    /*
    panic_if(vc_busy_counter[vnet] > m_deadlock_threshold,
        "%s: Possible network deadlock in vnet: %d at time: %llu \n",
        name(), vnet, curTick());
    */

    return -1;
}


/** This function looks at the NI buffers
 *  if some buffer has flits which are ready to traverse the link in the next
 *  cycle, and the downstream output vc associated with this flit has buffers
 *  left, the link is scheduled for the next cycle
 */

void
NetworkInterface::scheduleOutputLink()
{
    int vc = m_vc_round_robin;

    for (int i = 0; i < m_num_vcs; i++) {
        vc++;
        if (vc == m_num_vcs)
            vc = 0;

        // model buffer backpressure
        if (m_ni_out_vcs[vc]->isReady(curCycle()) &&
            m_out_vc_state[vc]->has_credit()) {

            bool is_candidate_vc = true;
            int t_vnet = get_vnet(vc);
            int vc_base = t_vnet * m_vc_per_vnet;

            if (m_net_ptr->isVNetOrdered(t_vnet)) {
                for (int vc_offset = 0; vc_offset < m_vc_per_vnet;
                     vc_offset++) {
                    int t_vc = vc_base + vc_offset;
                    if (m_ni_out_vcs[t_vc]->isReady(curCycle())) {
                        if (m_ni_out_vcs_enqueue_time[t_vc] <
                            m_ni_out_vcs_enqueue_time[vc]) {
                            is_candidate_vc = false;
                            break;
                        }
                    }
                }
            }
            if (!is_candidate_vc)
                continue;

            m_vc_round_robin = vc;

            m_out_vc_state[vc]->decrement_credit();
            // Just removing the flit
            flit *t_flit = m_ni_out_vcs[vc]->getTopFlit();
            t_flit->set_time(curCycle() + Cycles(1));
            outFlitQueue->insert(t_flit);
            // schedule the out link
            outNetLink->scheduleEventAbsolute(clockEdge(Cycles(1)));

            if (t_flit->get_type() == TAIL_ ||
               t_flit->get_type() == HEAD_TAIL_) {
                m_ni_out_vcs_enqueue_time[vc] = Cycles(INFINITE_);
            }
            return;
        }
    }
}

int
NetworkInterface::get_vnet(int vc)
{
    for (int i = 0; i < m_virtual_networks; i++) {
        if (vc >= (i*m_vc_per_vnet) && vc < ((i+1)*m_vc_per_vnet)) {
            return i;
        }
    }
    fatal("Could not determine vc");
}


// Wakeup the NI in the next cycle if there are waiting
// messages in the protocol buffer, or waiting flits in the
// output VC buffer
void
NetworkInterface::checkReschedule()
{
    for (const auto& it : inNode_ptr) {
        if (it == nullptr) {
            continue;
        }

        while (it->isReady(clockEdge())) { // Is there a message waiting
            scheduleEvent(Cycles(1));
            return;
        }
    }

    for (int vc = 0; vc < m_num_vcs; vc++) {
        if (m_ni_out_vcs[vc]->isReady(curCycle() + Cycles(1))) {
            scheduleEvent(Cycles(1));
            return;
        }
    }

    //for task graph, every cycle wake up the NI
    scheduleEvent(Cycles(1));
}

void
NetworkInterface::print(std::ostream& out) const
{
    out << "[Network Interface]";
}

uint32_t
NetworkInterface::functionalWrite(Packet *pkt)
{
    uint32_t num_functional_writes = 0;
    for (unsigned int i  = 0; i < m_num_vcs; ++i) {
        num_functional_writes += m_ni_out_vcs[i]->functionalWrite(pkt);
    }

    num_functional_writes += outFlitQueue->functionalWrite(pkt);
    return num_functional_writes;
}

NetworkInterface *
GarnetNetworkInterfaceParams::create()
{
    return new NetworkInterface(this);
}

//for task graph traffic
int
NetworkInterface::add_task(GraphTask &t){
    task_list.push_back(t);
    return 0;
}

int
NetworkInterface::sort_task_list()
{
    sort( task_list.begin(), task_list.end(), compare);
    return 0;
}

int
NetworkInterface::get_task_offset_by_task_id(int tid)
{
    for (unsigned int i=0; i<task_list.size(); i++)
        {
                GraphTask &e = task_list.at(i) ;
                if (e.get_id() == tid)
                        return i;
        }
    fatal(" Error in finding task offset by task id ! ");
}

GraphTask&
NetworkInterface::get_task_by_task_id(int tid)
{
    for (unsigned int i=0; i<task_list.size(); i++)
        {
                GraphTask &e = task_list.at(i) ;
                if (e.get_id() == tid)
                        return e;
        }
    fatal(" Error in finding task by task id ! ");
}

void
NetworkInterface::task_execution()
{
    if (task_list.size()<=0)
                        return;

    int current_task_id;
    if (task_in_waiting_list.size() == 0){
        task_in_waiting_list.push_back(task_list.at(0).get_id());
        waiting_list_offset = 0;
    }

    current_task_id = task_in_waiting_list.at(waiting_list_offset);
    GraphTask &c_task = get_task_by_task_id(current_task_id);

    switch (c_task.get_task_state())
    {
    case 0://idle
    {
        if (c_task.get_completed_times() >= c_task.get_required_times())
        {
            task_in_waiting_list.erase(task_in_waiting_list.begin() \
                + waiting_list_offset);
            if (waiting_list_offset >= task_in_waiting_list.size())
                waiting_list_offset = 0;
            break;
        }

        int j;
        for (j = 0; j < c_task.get_size_of_outgoing_edge_list(); j++)
        {
            GraphEdge &edge_temp = c_task.get_outgoing_edge_by_offset(j);
            if (edge_temp.get_out_memory_remained() <= 0)
                break;
        }
        if (j < c_task.get_size_of_outgoing_edge_list())
        {
            waiting_list_offset = (waiting_list_offset + 1) % \
            task_in_waiting_list.size();
            break;
            //output buffer not ready
        }

        //the starting task without dependency on other tasks
        if (c_task.get_size_of_incoming_edge_list() == 0)
        {
            c_task.set_task_state(1);
            //Note here
            remained_execution_time = c_task.get_random_execution_time();

            for (int j = 0; j < c_task.get_size_of_outgoing_edge_list(); j++)
            {
                GraphEdge &edge_temp = c_task\
                    .get_outgoing_edge_by_offset(j);
                assert(edge_temp.update_out_memory_write_pointer());

                int dest_proc_id = c_task.get_outgoing_edge_by_offset(j)\
                    .get_dst_proc_id();
                if (dest_proc_id == c_task.get_proc_id())
                {
                    assert(dest_proc_id == m_id);
                    /*comment because we not use in memory
                    int dest_task_id = c_task.get_outgoing_edge_by_offset(j)\
                        .get_dst_task_id();
                    int edge_id = c_task.get_outgoing_edge_by_offset(j)\
                        .get_id();
                    GraphTask &dst_task = get_task_by_task_id(dest_task_id);
                    GraphEdge &in_edge = dst_task\
                        .get_incoming_edge_by_eid(edge_id);
                    assert(in_edge.update_in_memory_write_pointer());
                    */
                }

                int num_flits = ceil((double)edge_temp\
                    .get_random_token_size() /\
                    (m_net_ptr->getNiFlitSize() * 8));

                /*
                DPRINTF(TaskGraph, "NI %d task %d excuting\n",\
                m_id, c_task.get_id());
                */
                enqueueFlitsGeneratorBuffer(edge_temp, num_flits);
               /*
                DPRINTF(TaskGraph, "NI %d Task %d Edge %d equeue %d \
                flits in Generator Buffer.\n",m_id, c_task.get_id(), \
                edge_temp.get_id() ,num_flits);
                */

                edge_temp.generate_new_token();
            }
            break;

        } else {// the task that depends on other tasks
            int j;
            for (j=0;j<c_task.get_size_of_incoming_edge_list();j++){
                GraphEdge &edge_temp=c_task.get_incoming_edge_by_offset(j);
                if (edge_temp.get_num_incoming_token()>0)//there is token
                    continue;
                else
                    break;
                    //the requirement is not satisfied; we wait
            }
            if (j < c_task.get_size_of_incoming_edge_list()){
                waiting_list_offset=(waiting_list_offset+1)%\
                task_in_waiting_list.size();
                break;
                //not satisied, jump to next candidate, wait next cycle
                        }

           /*
           DPRINTF(TaskGraph, "NI %d task %d has received all token\n",\
            m_id,c_task.get_id());
            */

            for (j=0;j< c_task.get_size_of_incoming_edge_list();j++){
                GraphEdge &tempInEdge=c_task.get_incoming_edge_by_offset(j);
                /*
                DPRINTF(TaskGraph, "token num is %d\n", \
                tempInEdge.get_num_incoming_token());
                */
                tempInEdge.consume_token();//consume the token

                //assert(tempInEdge.update_in_memory_read_pointer());
                int src_proc_id=tempInEdge.get_src_proc_id();
                if (src_proc_id==c_task.get_proc_id()){
                    assert(src_proc_id==m_id);
                    int src_task_id=tempInEdge.get_src_task_id();
                    int edge_id=tempInEdge.get_id();
                    GraphTask &src_task= get_task_by_task_id(src_task_id);
                    GraphEdge &out_edge=src_task.\
                    get_outgoing_edge_by_eid(edge_id);
                    assert(out_edge.update_out_memory_read_pointer());
                } else {
                    //previous: to send a control type to src_task
                }
            }

            c_task.set_task_state(1);
            remained_execution_time=c_task.get_random_execution_time();

            for (j=0;j< c_task.get_size_of_outgoing_edge_list();j++){
                GraphEdge &edge_temp=c_task.get_outgoing_edge_by_offset(j);
                assert(edge_temp.update_out_memory_write_pointer());

                int dest_proc_id=c_task.get_outgoing_edge_by_offset(j).\
                get_dst_proc_id();
                if (dest_proc_id==c_task.get_proc_id()){
                    assert(dest_proc_id==m_id);
                    /*comment because we not use in_memory
                    int dest_task_id=c_task.get_outgoing_edge_by_offset(j).\
                    get_dst_task_id();
                    int edge_id=c_task.get_outgoing_edge_by_offset(j).get_id();
                    GraphTask &dst_task= get_task_by_task_id(dest_task_id);
                    GraphEdge &in_edge=dst_task.\
                    get_incoming_edge_by_eid(edge_id);
                    //assert(in_edge.update_in_memory_write_pointer());
                    */
                }

                int num_flits = ceil((double)edge_temp\
                .get_random_token_size() /(m_net_ptr->getNiFlitSize() * 8));

                enqueueFlitsGeneratorBuffer(edge_temp, num_flits);
                edge_temp.generate_new_token();
            }
            break;
        }
        break;//break the switch
    }
    case 1://task execution
    {
        remained_execution_time--;

        if (remained_execution_time<=0){
        /*
        DPRINTF(TaskGraph, "NI %d Task %d remained execution time is %d\n",\
        m_id, c_task.get_id(), remained_execution_time);
        */
            c_task.set_task_state(0);
            remained_execution_time=0;

            c_task.add_completed_times();

        /*
            DPRINTF(TaskGraph, "NI %d Task %d Execute completely !\n", \
            m_id, c_task.get_id());
        */

            task_in_waiting_list.erase(task_in_waiting_list.begin()+\
            waiting_list_offset);

            if (waiting_list_offset>=task_in_waiting_list.size())
                waiting_list_offset=0;

            int task_offset=get_task_offset_by_task_id(current_task_id);
            if (task_offset==0)
                task_in_waiting_list.push_back(current_task_id);

            task_offset++;
            if (task_offset>=task_list.size()){

            } else {
                task_in_waiting_list.push_back(task_list.\
                at(task_offset).get_id());
            }
        }
        break;
    }

    }
}

void
NetworkInterface::enqueueFlitsGeneratorBuffer( GraphEdge &e, int num ){
//actually enqueue the head flit in the Buffer, if triggerred, the Buffer
//generate the body flits
    RouteInfo route;
    route.vnet = 2;
    route.src_ni = m_id;
    route.src_router = m_router_id;
    route.dest_ni = e.get_dst_proc_id();
    //route.dest_router = route.dest_ni;
    route.dest_router = m_net_ptr->get_router_id(route.dest_ni);
    route.hops_traversed = -1;
    route.vc_chioce = (route.dest_router >= route.src_router);

    //specify the destinition
    NetDest net_dest;
    NodeID destID = (NodeID) route.dest_ni;

    for (int m = 0;m < (int) MachineType_NUM; m++) {
        if ((destID >= MachineType_base_number((MachineType) m)) &&
                destID < MachineType_base_number((MachineType) (m+1))) {
            // calculating the NetDest associated with this dest_ni
            net_dest.clear();
            net_dest.add((MachineID) {(MachineType) m, (destID -
                        MachineType_base_number((MachineType) m))});
            //net_msg_ptr->getDestination() = net_dest;
            break;
        }
    }
    route.net_dest = net_dest;

    MsgPtr msg_ptr=NULL;

    //token length in packet
    int num_packets = ceil((double)num/m_net_ptr->getTokenLenInPkt());

    TGInfo tg;
    tg.src_task = e.get_src_task_id();
    tg.dest_task = e.get_dst_task_id();
    tg.edge_id = e.get_id();
    tg.token_id = e.get_current_token_id();
    tg.token_length_in_pkt = num_packets;
    //DPRINTF(TaskGraph,"\n");
/*
DPRINTF(TaskGraph, "NI %d Task %d Edge %d equeue %d packets \
in Generator Buffer.\n",\
                m_id, tg.src_task, e.get_id() ,num_packets);
*/

    int temp_time_to_generate = 0;
    //generator_buffer_type *buffer_temp = new generator_buffer_type;
    for (int i = 0; i < num_packets; i++)
    {
        int num_flits = m_net_ptr->getTokenLenInPkt();

        if (i==num_packets-1){
            num_flits = num - (num_packets-1)*m_net_ptr->getTokenLenInPkt();
            num_flits = (num_flits >= m_net_ptr->getBuffersPerDataVC())\
            ?num_flits:m_net_ptr->getBuffersPerDataVC();
            /*DPRINTF(TaskGraph, " num flits = %d, buffer depth = %d\n ",\
             num_flits, m_net_ptr->getBuffersPerDataVC());
             */
        }

        //vnet2 is response vnet
        flit *fl = new flit(0, -1, 2, route, num_flits, \
        msg_ptr, curCycle(), tg);
        temp_time_to_generate += e.get_random_pkt_interval();
        //use enqueue time as the time it should have been sent, for the src
        //delay in queue latency
        fl->set_enqueue_time(curCycle() + Cycles(temp_time_to_generate - 1));
        DPRINTF(TaskGraph,\
        "NI %d flit %d generate after %d cycles in Cycle [%lu]\n", m_id,\
        i, temp_time_to_generate, \
        u_int64_t(curCycle() + Cycles(temp_time_to_generate - 1)));

        generator_buffer_type *buffer_temp = new generator_buffer_type;
        buffer_temp->flit_to_generate = fl;
        buffer_temp->time_to_generate_flit = temp_time_to_generate;
        generator_buffer.push_back( buffer_temp );
    }
}

void
NetworkInterface::updateGeneratorBuffer(){
    for (unsigned int i=0;i<generator_buffer.size();i++){
        generator_buffer.at(i)->time_to_generate_flit--;

        DPRINTF(TaskGraph,"NI %d Generator buffer flit %d \
        generate after %d cycles\n", \
        m_id, i, generator_buffer.at(i)->time_to_generate_flit);


        if (generator_buffer.at(i)->time_to_generate_flit<=0){
            //the head flit
            flit *fl = generator_buffer.at(i)->flit_to_generate;

            //if the dest core is the same core
            if (fl->get_route().src_ni == fl->get_route().dest_ni){
                assert(fl->get_route().dest_ni == m_id);

                GraphTask& dest_task = get_task_by_task_id(fl->\
                get_tg_info().dest_task);
                GraphEdge& dest_edge = dest_task.get_incoming_edge_by_eid(fl->\
                get_tg_info().edge_id);

                dest_edge.record_pkt(fl);
                generator_buffer.erase(generator_buffer.begin()+i);
                i--;
                continue;
            }

            int vc=calculateVC(fl->get_vnet());

            if (vc == -1)
                continue;
            //without avilable vc, next flit

            //check the buffer in the dest core
            GraphTask& src_task = get_task_by_task_id(fl->\
            get_tg_info().src_task);
            GraphEdge& src_edge = src_task.get_outgoing_edge_by_eid\
            (fl->get_tg_info().edge_id);

            if (! src_edge.record_sent_pkt(fl))
                continue;

            int num_flits = fl->get_size();

            for (int j=0;j<num_flits;j++){
                flit* generated_fl = new flit(j, vc, 2, fl->get_route(), \
                num_flits, fl->get_msg_ptr(),curCycle(), fl->get_tg_info());

                DPRINTF(TaskGraph, "NI %d Flit should send time in %lu\n",\
                 m_id, uint64_t(fl->get_enqueue_time()));
                generated_fl->set_src_delay(curCycle() - \
                fl->get_enqueue_time());

                m_ni_out_vcs[vc]->insert(generated_fl);
            }

            m_ni_out_vcs_enqueue_time[vc] = curCycle();
            m_out_vc_state[vc]->setState(ACTIVE_, curCycle());

         /*
         DPRINTF(TaskGraph, " flits from NI %d Task %d inject to \
         vc %d to dst_ni %d \n", m_id, fl->get_tg_info().src_task, vc, \
         fl->get_route().dest_ni);
         */

            generator_buffer.erase(generator_buffer.begin()+i);
            i--;
        }
    }
}
