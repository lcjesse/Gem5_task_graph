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


#ifndef __MEM_RUBY_NETWORK_GARNET2_0_NETWORKINTERFACE_HH__
#define __MEM_RUBY_NETWORK_GARNET2_0_NETWORKINTERFACE_HH__

#include <iostream>
#include <vector>

#include "mem/ruby/common/Consumer.hh"
#include "mem/ruby/network/garnet2.0/CommonTypes.hh"
#include "mem/ruby/network/garnet2.0/CreditLink.hh"
#include "mem/ruby/network/garnet2.0/GarnetNetwork.hh"
#include "mem/ruby/network/garnet2.0/NetworkLink.hh"
#include "mem/ruby/network/garnet2.0/OutVcState.hh"
#include "mem/ruby/slicc_interface/Message.hh"
#include "params/GarnetNetworkInterface.hh"

class MessageBuffer;
class flitBuffer;

class NetworkInterface : public ClockedObject, public Consumer
{
  public:
    typedef GarnetNetworkInterfaceParams Params;
    NetworkInterface(const Params *p);
    ~NetworkInterface();

    void init();

    void addInPort(NetworkLink *in_link, CreditLink *credit_link);
    void addOutPort(NetworkLink *out_link, CreditLink *credit_link,
        SwitchID router_id);

    void dequeueCallback();
    void wakeup();
    void addNode(std::vector<MessageBuffer *> &inNode,
                 std::vector<MessageBuffer *> &outNode);

    void print(std::ostream& out) const;
    int get_vnet(int vc);
    int get_router_id() { return m_router_id; }
    void init_net_ptr(GarnetNetwork *net_ptr) { m_net_ptr = net_ptr; }

    uint32_t functionalWrite(Packet *);

    //for task graph traffic
    int add_task(GraphTask &t);
    int	sort_task_list();
    int get_task_offset_by_task_id(int core_id, int tid);
    GraphTask& get_task_by_task_id(int core_id, int tid);
    NodeID get_ni_id() { return m_id; }
    unsigned int get_task_list_length(int idx) { return task_list[idx].size(); }
    GraphTask& get_task_by_offset(int core_id, int i){
      int idx = lookUpMap(m_core_id_index, core_id);
      return task_list[idx][i];
    }
    //muilt core
    int get_core_id_by_task_id(int tid);
    int get_num_cores(){ return m_num_cores; }
    int get_core_id_by_index(int i);
    std::string get_core_name_by_index(int i);

    void task_execution();

    //for construct architecture in tg mode
    bool configureNode(int num_cores, int* core_id, \
    std::string* core_name, int* num_threads);
    void printNodeConfiguation();
    int lookUpMap(std::map<int, int> m, int idx);
    
  private:
    GarnetNetwork *m_net_ptr;
    const NodeID m_id;
    const int m_virtual_networks, m_vc_per_vnet, m_num_vcs;
    int m_router_id; // id of my router
    std::vector<OutVcState *> m_out_vc_state;
    std::vector<int> m_vc_allocator;
    int m_vc_round_robin; // For round robin scheduling
    flitBuffer *outFlitQueue; // For modeling link contention
    flitBuffer *outCreditQueue;
    int m_deadlock_threshold;

    NetworkLink *inNetLink;
    NetworkLink *outNetLink;
    CreditLink *inCreditLink;
    CreditLink *outCreditLink;

    // Queue for stalled flits
    std::deque<flit *> m_stall_queue;
    std::vector<int> m_stall_count;

    // Input Flit Buffers
    // The flit buffers which will serve the Consumer
    std::vector<flitBuffer *>  m_ni_out_vcs;
    std::vector<Cycles> m_ni_out_vcs_enqueue_time;

    // The Message buffers that takes messages from the protocol
    std::vector<MessageBuffer *> inNode_ptr;
    // The Message buffers that provides messages to the protocol
    std::vector<MessageBuffer *> outNode_ptr;
    // When a vc stays busy for a long time, it indicates a deadlock
    std::vector<int> vc_busy_counter;

    bool checkStallQueue();
    bool flitisizeMessage(MsgPtr msg_ptr, int vnet);
    int calculateVC(int vnet);

    void scheduleOutputLink();
    void checkReschedule();
    void sendCredit(flit *t_flit, bool is_free);

    void incrementStats(flit *t_flit);

    //for task graph traffic
    //task_list in each core
    std::vector<std::vector<GraphTask> > task_list;
    std::vector<std::vector<int> > task_in_waiting_list;
    std::vector<int> waiting_list_offset;

    //for construct architecture in tg mode
    int m_num_cores;
    std::map<int, int> m_index_core_id;
    std::map<int, int> m_core_id_index; //core_id -> task list index
    std::map<int, std::string> m_core_id_name; //core_id -> core name
    std::map<int, int> m_core_id_thread;//core_id -> num_threads

    //buffer for each core and 
    //for inter-cluster and intra-cluster communication
    std::vector<std::vector<flit* > > core_buffer;
    std::vector<bool > crossbar_busy_out;
    std::vector<int > crossbar_delay_timer;
    std::vector<std::vector<flit* > > crossbar_data;
    int core_buffer_round_robin;
    const int crossbar_delay = 2;


    struct _compare_task
    {
                bool
    operator() (GraphTask t1, GraphTask t2)
    {
      return (t1.get_schedule() < t2.get_schedule());
    }
        } compare;

    //Generator Buffer for each Core, can be considered as the running Core
    std::vector< std::vector<generator_buffer_type* >> generator_buffer;

    //remained execution time in each core
    std::vector<int> remained_execution_time;

    void enqueueFlitsGeneratorBuffer(GraphEdge &, int num_flits);
    void updateGeneratorBuffer();

    void coreSendFlitsOut();
};

#endif // __MEM_RUBY_NETWORK_GARNET2_0_NETWORKINTERFACE_HH__
