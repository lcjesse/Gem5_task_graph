#include "mem/ruby/network/garnet2.0/GraphTask.hh"

GraphEdge&
GraphTask::get_incoming_edge_by_eid(int eid)
{
        for (unsigned int i = 0; i < incoming_edge_list.size(); i++)
        {
                GraphEdge &e = incoming_edge_list.at(i);
                if (e.get_id() == eid)
                        return e;
        }
        fatal(" Cannot find the incoming edge by edge id ! ");
}

GraphEdge&
GraphTask::get_incoming_edge_by_offset(int i)
{
        GraphEdge &e = incoming_edge_list.at(i);
        return e;
}

GraphEdge&
GraphTask::get_outgoing_edge_by_eid(int eid)
{
        for (unsigned int i = 0; i < outgoing_edge_list.size(); i++)
        {
                GraphEdge &e = outgoing_edge_list.at(i);
                if (e.get_id() == eid)
                        return e;
        }
        fatal(" Cannot find the outgoing edge by edge id ! ");
}

GraphEdge&
GraphTask::get_outgoing_edge_by_offset(int i)
{
        GraphEdge &e = outgoing_edge_list.at(i);
        return e;
}

int
GraphTask::add_incoming_edge(GraphEdge &e)
{
        incoming_edge_list.push_back(e);
        return 0;
}

int
GraphTask::add_outgoing_edge(GraphEdge &e)
{
        outgoing_edge_list.push_back(e);
        return 0;
}

int
GraphTask::get_random_execution_time()
{
        int a = gen_normal_dist(mu_time, sigma_time);
        if (a > max_time)
                a = max_time;
        else if (a <= 0)
                a = 1;
        return a;
}

int
GraphTask::set_statistical_execution_time(double mu, double sigma)
{
        assert(mu > 0 && sigma > 0);
        mu_time = mu;
        sigma_time = sigma;

        return 0;
}

int
GraphTask::set_id(int tid)
{
        assert(tid >= 0);
        id = tid;

        return 0;
}

int
GraphTask::set_proc_id(int pid)
{
        assert(pid >= 0);
        proc_id = pid;

        return 0;
}

int
GraphTask::set_schedule(int s)
{
        assert(s >= 0);
        schedule = s;

        return 0;
}

int
GraphTask::set_max_time(int t)
{
        assert(t > 0);
        max_time = t;

        return 0;
}
