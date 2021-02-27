#ifndef __MEM_RUBY_NETWORK_GARNET2_0_GRAPH_EDGE_HH__
#define __MEM_RUBY_NETWORK_GARNET2_0_GRAPH_EDGE_HH__

#include <cassert>
#include <iostream>
#include <vector>

#include "mem/ruby/network/garnet2.0/TaskGraphDefinition.hh"
#include "mem/ruby/network/garnet2.0/flit.hh"

class GraphEdge
{
public:
        // critical functions for the statistical trace
        // get a random token size using the parameters for
                // Gaussian distribution
        int get_random_token_size();
        // get a random packet generation interval
        //using the parameter for Exponential distribution
        int get_random_pkt_interval();
        //notice: it is not related with pkt size.
        //lambda=num_pkts(event)/task_execution_time

        // basic functions to operate on the basic parameters
        int get_id();
        int set_id(int eid);

        int get_src_task_id();
        int set_src_task_id(int tid);
        int get_dst_task_id();
        int set_dst_task_id(int tid);

        int get_src_proc_id();
        int set_src_proc_id(int pid);
        int get_dst_proc_id();
        int set_dst_proc_id(int pid);

        int set_vc_choice(int vid);    // Set in GarnetNetwork
        int get_vc_choice();    // Return vc_choice for NI

        int get_max_token_size();
        int set_max_token_size(int size);

        double get_mu() { return mu_token_size; }
        double get_sigma() { return sigma_token_size; }
        double get_lambda() { return lambda_pkt_interval; }

        //set incoming token size
        void set_token_size(int token_size);

        int get_num_incoming_token() { return num_incoming_token; }

        void
        consume_token()
        {
                num_incoming_token = num_incoming_token - 1;
                return;
        }

        int set_statistical_token_size(double mu, double sigma);
        int set_statistical_pkt_interval(double lambda);
        int set_recorded_token_size(int s);

        void initial();

        //record the incoming token/pkt
        int record_pkt(flit* pkt, int time);
        //for compare all in edge's token receive time, choose the max time
        //it will compare the first token the edge have, and delete it after
        //it is used.
        int get_token_received_time(){
                //now the token has been consume
                assert(token_receive_time.size() >= num_incoming_token + 1);
                int time = token_receive_time.front();
                token_receive_time.erase(token_receive_time.begin());
                token_receive_time.shrink_to_fit();

                return time;
        }

        //when the edge is outgoing edge, we keep the ID of current token
        int
        generate_new_token()
        {
                output_token_id++;
                return output_token_id;
        }

        int get_current_token_id() { return output_token_id; }

        std::vector<int> &get_pkt_generate_time() { return pkt_generate_time; }

        void
        set_out_memory(int a, int b)
        {
                out_memory_start_address = a;
                out_memory_size = b;
                out_memory_remained = out_memory_size;
                out_memory_write_pointer = 0;
                out_memory_read_pointer = 0;
                return;
        }

        bool
        update_out_memory_write_pointer()
        {
                if (out_memory_remained <= 0)
                        return false;
                out_memory_write_pointer = (out_memory_write_pointer + 1) \
                % out_memory_size;
                out_memory_remained--;
                return true;
        }

        bool
        update_out_memory_read_pointer()
        {
                if (out_memory_remained >= out_memory_size)
                        return false;
                out_memory_read_pointer = (out_memory_read_pointer + 1) \
                % out_memory_size;
                out_memory_remained++;
                return true;
        }
        int get_out_memory_remained() { return out_memory_remained; }
        int get_out_memory_size() { return out_memory_size; }

        void
        set_in_memory(int a, int b)
        {
                in_memory_start_address = a;
                in_memory_size = b;
                in_memory_remained = in_memory_size;
                in_memory_write_pointer = 0;
                in_memory_read_pointer = 0;
                return;
        }

        bool
        update_in_memory_write_pointer()
        {
                if (in_memory_remained <= 0)
                        return false;
                in_memory_write_pointer = (in_memory_write_pointer + 1) \
                % in_memory_size;
                in_memory_remained--;
                return true;
        }

        bool
        update_in_memory_read_pointer()
        {
                if (in_memory_remained >= in_memory_size)
                        return false;
                in_memory_read_pointer = (in_memory_read_pointer + 1) \
                                % in_memory_size;
                in_memory_remained++;
                return true;
        }

        int get_in_memory_remained() { return in_memory_remained; }
        int get_in_memory_write_pointer() { return in_memory_write_pointer; }
        int get_in_memory_size() { return in_memory_size; }

        bool record_sent_pkt(flit* pkt);

        /* Memory operation is as below:
        Execute_task: task's in_edge's in_memory_read, if the src_task is
                mapped to the same core as current task,
                                the src_task's out_edge's
                out_memory_read is also updated task's
                                out_edge's out_memory_write,
                if the desk_task is mapped to the same core as current task,
                the dest_task's in_edge's in_memory_write is also updated
        Send_data_out: if both tasks of the out_edge are on the same core, do
        nothing; else, src_task's out_edge's out_memory_read
        receive_data: if both tasks of the out_edge are on the same core, do
        nothing; else, dest_task's in_edge's in_memory_write
        */

       //for multi-app
        void set_app_idx(int i){ app_idx=i; return; }
        int get_app_idx() { return app_idx; }
        //decide whether the flit in this edge token list
        bool find_in_token_list(flit* fl) {
                        int i;
                        // find token
                        for (i = 0; i < received_token_list.size(); i++)
                        {
                                if (received_token_list.at(i).id ==
                                        fl->get_tg_info().token_id)
                                {
                                        break;
                                }
                        }
                        //new token
                        if (i >= received_token_list.size())
                        {
                                return false;
                        } else {
                                return true;
                        }
                }

        int get_total_incoming_token(){ return total_incoming_token; }

private:
        // the statistical token sizes follow Gaussian distribution
        double mu_token_size;	 // the mean of the token size
        double sigma_token_size; // the sd of the token size

        // the statistical packet generation intervals
        //follow Exponential distribution
        // the rate parameter, the inverse of
                // the average packet generation interval
        double lambda_pkt_interval;

        // basic parameters
        int id;				// the id of the edge
        int src_task_id;	// the id of the source task
        int dst_task_id;	// the id of the destination task
        int src_proc_id;	// the id of the PU the source task is assigned
        int dst_proc_id;    // the id of the PU the destination task

        int vc_choice;     // vc choice for vc allocation, set in GarnetNetwork

        // the maximum possible token size generated by the execution
        //of the source task
        int max_token_size;

        // the number of token which has come as a whole token
        int num_incoming_token;
        // current total num of token which for compute task waiting time
        int total_incoming_token;
        std::vector<int> token_receive_time;

        //the number of partially received tokens
        std::vector<token_info_type> received_token_list;

        //the number of partially sent tokens
        std::vector<token_info_type> sent_token_list;

        //the output token ID
        int output_token_id;

        std::vector<int> pkt_generate_time;

        // the start address to write data for outgoing edge
        int out_memory_start_address;
        int out_memory_size;
        int out_memory_write_pointer;
        int out_memory_read_pointer;
        int out_memory_remained;

        // the start address to write data for outgoing edge
        int in_memory_start_address;
        int in_memory_size;
        int in_memory_write_pointer;
        int in_memory_read_pointer;
        int in_memory_remained;

        //for multi-app
        int app_idx;
};


#endif

