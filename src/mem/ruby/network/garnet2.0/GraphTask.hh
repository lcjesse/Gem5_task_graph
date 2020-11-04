#ifndef __MEM_RUBY_NETWORK_GARNET2_0_GRAPH_TASK_HH__
#define __MEM_RUBY_NETWORK_GARNET2_0_GRAPH_TASK_HH__

#include "mem/ruby/network/garnet2.0/GraphEdge.hh"

class GraphTask
{
public:
        // critical functions for the statistical trace
        // get a random execution time using the parameters
        // for Gaussian distribution
        int get_random_execution_time();
        int set_statistical_execution_time(double mu, double sigma);

        // assistant functions
        int add_incoming_edge(GraphEdge &e);
        int add_outgoing_edge(GraphEdge &e);

        // basic functions
        int get_id() { return id; }
        int set_id(int tid);

        int get_proc_id() { return proc_id; }
        int set_proc_id(int pid);

        int get_schedule() { return schedule; }
        int set_schedule(int s);

        int get_max_time() { return max_time; }
        int set_max_time(int t);

        double get_mu() { return mu_time; }
        double get_sigma() { return sigma_time; }

        GraphEdge &get_incoming_edge_by_eid(int eid);
        GraphEdge &get_incoming_edge_by_offset(int eid);
        GraphEdge &get_outgoing_edge_by_eid(int eid);
        GraphEdge &get_outgoing_edge_by_offset(int eid);
        int
        get_size_of_incoming_edge_list() { return incoming_edge_list.size(); }
        int
        get_size_of_outgoing_edge_list() { return outgoing_edge_list.size(); }

        int
        set_required_times(int k)
        {
                required_times = k;
                return 0;
        }

        int get_required_times() { return required_times; }

        int get_c_e_times() {return c_e_times;}
        void add_c_e_times() { c_e_times++;}

        void
        initial()
        {
                completed_times = 0;
                task_state = 0;
                c_e_times = 0;
                return;
        }

        void add_completed_times() { completed_times++; }
        int get_completed_times() { return completed_times; }

        void
        set_task_state(int i)
        {
                task_state = i;
                return;
        }
        int get_task_state() { return task_state; }
        void record_execution_time(int start, int end){
                start_time.push_back(start);end_time.push_back(end);
        }
        int get_start_time(int i){return start_time.at(i);}
        int get_end_time(int i){return end_time.at(i);}
        void set_all_tokens_received_time(int time){
                get_all_tokens_time.push_back(time);
        }
        int get_task_waiting_time(int i){
                return start_time[i]-get_all_tokens_time[i];}
        int get_token_received_size(){ return get_all_tokens_time.size(); }
        void set_app_idx(int i){ app_idx=i; return; }
        int get_app_idx() { return app_idx; }

private:
        // the statistical task executions follow Gaussian distribution
        double mu_time;	   // the mean of the task execution time
        double sigma_time; // the sd of the task execution time

        // basic parameters
        int id;		  // the id of the task
        int proc_id;  // the id of the PU the task is assigned
        // the sequence number the task is assigned to execute on the PU
        int schedule;
        int max_time; // the worst-case execution time of the task

        // for multi-application
        int app_idx;

        // each entry is an incoming edge
        std::vector<GraphEdge> incoming_edge_list;
        // each entry is an outgoing edge
        std::vector<GraphEdge> outgoing_edge_list;
        int completed_times; //the times that this task has been finished
        //the times required for this this task.
        //In this application, it is always 1.
        int required_times;

        int task_state;
        //For a task, first get all tokens, then if core idle, the task begin
        //execute, so between them could be the task waiting time.
        std::vector<int> get_all_tokens_time;
        std::vector<int> start_time;
        std::vector<int> end_time;

        //the times completed or executing
        int c_e_times;
};


#endif
