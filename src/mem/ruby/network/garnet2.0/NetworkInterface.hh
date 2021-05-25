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
    int add_task(int app_idx, GraphTask &t, bool is_head_task);
    int	sort_task_list();
    int get_task_offset_by_task_id(int core_id, int app_idx, int tid);
    GraphTask& get_task_by_task_id(int core_id, int app_idx, int tid);
    NodeID get_ni_id() { return m_id; }
    unsigned int get_task_list_length(int idx, int app_idx){
      return task_list[idx][app_idx].size(); }
    GraphTask& get_task_by_offset(int core_id, int app_idx, int i){
      int idx = lookUpMap(m_core_id_index, core_id);
      return task_list[idx][app_idx][i];
    }
    //muilt core
    int get_core_id_by_task_id(int app_idx, int tid);
    int get_num_cores(){ return m_num_cores; }
    int get_core_id_by_index(int i);
    std::string get_core_name_by_index(int i);

    void enqueueTaskInThreadQueue();
    void task_execution();

    //for construct architecture in tg mode
    bool configureNode(int num_cores, int* core_id, \
    std::string* core_name, int* num_threads, int num_apps);
    void printNodeConfiguation();
    int lookUpMap(std::map<int, int> m, int idx);

    // // when token is all consumed, reset to fixed value
    // void reset_initial_app_ratio_token(){
    //   for(int i = 0; i < m_num_apps; i++){
    //     initial_app_ratio_token[i] = fixed_initial_app_ratio_token[i];
    //   }
    // }
    // void reset_initial_app_ratio_token(){
    //   for(int i = 0; i < m_num_apps; i++){
    //     if(i==0){
    //       initial_app_ratio_token[i] = 1;
    //     }else{
    //       initial_app_ratio_token[i] = 5;
    //     }
    //   }
    // }

    //for throughput
    double get_throughput(int core_id){
      int core_idx = lookUpMap(m_core_id_index, core_id);
      double throughput = m_total_data_bits[core_idx] / (curCycle());
      // unit is Gbps
      return throughput;
    }

    //
    int get_core_buffer_size(int core_idx){
      return (core_buffer[core_idx].size()+cluster_buffer[core_idx].size());
    }

    std::vector<int> core_buffer_sent;
    void initializeTaskIdList();
    // void initializeTaskBuffer();

    // // read Application Config file to initialize fixed_initial_app_ratio_token
    // void initializeFixedRatioToken(int *ratiolist){
    //   for(int i = 0; i < m_num_apps; i++){
    //     fixed_initial_app_ratio_token[i] = ratiolist[i];
    //   }
    // }

    int get_num_tokens(){
      if (m_id == 8){
        GraphTask &c_task = get_task_by_task_id(11, 0, 1);
        GraphEdge &e = c_task.get_incoming_edge_by_eid(0);
        return e.get_num_incoming_token();
      } else {
        return -2;
      }
    }

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
    //Get the remained vcs, make corebuffer can enqueue more flits in buffer
    int getNumRemainedIdleVC(int vnet);

    void scheduleOutputLink();
    void checkReschedule();
    void sendCredit(flit *t_flit, bool is_free);

    void incrementStats(flit *t_flit);
    void incrementStats(flit *t_flit, bool in_core);

    //for task graph traffic
    //task_list in each core
    std::vector<std::vector<std::vector<GraphTask> > > task_list;
    std::vector<std::vector<std::vector<GraphTask> > > head_task_list;
    std::vector<std::vector<std::vector<int> > > task_id_list;
    //std::vector<std::vector<int> > task_in_waiting_list;
    std::vector<int> waiting_list_offset;
    //thread_queue[num_cores][num_threads]
    int** task_in_thread_queue;
    int** remained_execution_time_in_thread;
    bool** thread_busy_flag;
    int** task_to_exec_round_robin;
    //for multi-app round robin
    int* app_exec_rr;
    int** app_idx_in_thread_queue;
    //
    int num_initial_thread;
    int* initial_task_thread_queue;
    int* remainad_initial_task_exec_time;
    bool* initial_task_busy_flag;
    int* app_idx_in_initial_thread_queue;
    // int* initial_app_ratio_token; //token for init task in different apps to reach certain ratio
    // int* fixed_initial_app_ratio_token;
    //record PE-7 position for initial task judgement in NI
    int entrance_NI;
    int entrance_core;
    int entrance_idx_in_NI;

    //for construct architecture in tg mode
    int m_num_cores;
    std::map<int, int> m_index_core_id;
    std::map<int, int> m_core_id_index; //core_id -> task list index
    std::map<int, std::string> m_core_id_name; //core_id -> core name
    std::map<int, int> m_core_id_thread;//core_id -> num_threads
    //for multi-applications
    int m_num_apps;
    double* m_total_data_bits;

    //buffer for each core and
    //for intra-cluster communication
    std::vector<std::vector<flit* > > core_buffer;
    //for inter-cluster communication
    std::vector<std::vector<flit* > > cluster_buffer;
    std::vector<bool > crossbar_busy_out;
    std::vector<int > crossbar_delay_timer;
    std::vector<std::vector<flit* > > crossbar_data;
    int core_buffer_round_robin;
    const int crossbar_delay = 2;


    //for back pressure when core receive the flit
    std::vector<std::vector<flit* > > input_buffer; //core_num * buffer_size
    std::vector<int> input_buffer_size; //buffer_size
    const int not_used_token = 100;

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

    void enqueueFlitsGeneratorBuffer(GraphEdge &, int num_flits, \
      int task_execution_time);
    void updateGeneratorBuffer();

    void coreSendFlitsOut();
    void intraClusterOut();
    void interClusterOut();
};

#endif // __MEM_RUBY_NETWORK_GARNET2_0_NETWORKINTERFACE_HH__
