#include "mem/ruby/network/garnet2.0/GraphEdge.hh"

void
GraphEdge::initial()
{
        output_token_id = 0;
        num_incoming_token = 0;
        total_incoming_token = 0;
        generate_seed();
        gen_exp_dis_time(0.1);
        return;
}

int
GraphEdge::record_pkt(flit* fl, int time)
{
        int i;
        // find token
        for (i = 0; i < received_token_list.size(); i++)
        {
                if (received_token_list.at(i).id ==\
                fl->get_tg_info().token_id){
                        break;
                }
        }
        //new token
        if (i >= received_token_list.size())
        {
        //it consumes/reserves memory immediately,
        //However, it only applys when this is an inter-core pkt. Otherwise,
        //the memory is reserved already --in fact, data is located at the
        //same place
                if (src_proc_id != dst_proc_id)
                {
                        assert(update_in_memory_write_pointer());
                }
                token_info_type temp;
                temp.id = fl->get_tg_info().token_id;
                temp.length_in_pkt = fl->get_tg_info().token_length_in_pkt;
                temp.received_pkt = 1;
                received_token_list.push_back(temp);
        } else {
                if (received_token_list.at(i).length_in_pkt \
                                != fl->get_tg_info().token_length_in_pkt){
                        fatal("error receiving token when record flit ! ");
                        return 0;
                }
                received_token_list.at(i).received_pkt++;
        }
        //check token state
        if (received_token_list.at(i).received_pkt == \
                received_token_list.at(i).length_in_pkt)
        {
                num_incoming_token++;
                total_incoming_token++;
                token_receive_time.push_back(time);
                received_token_list.erase(received_token_list.begin() + i);
                received_token_list.shrink_to_fit();
                //if (id==0) printf("token size %d\n", num_incoming_token);
        } else if (received_token_list.at(i).received_pkt > \
                received_token_list.at(i).length_in_pkt) {
                fatal(" error receiving token when record flit ! ");
                return 0;
        }

        return 1;
}

bool
GraphEdge::record_sent_pkt(flit* fl)
{ //only for inter-core pkts
        int i;
        // find token
        for (i = 0; i < sent_token_list.size(); i++)
        {
                if (sent_token_list.at(i).id == fl->get_tg_info().token_id)
                {
                        break;
                }
        }
        //new token
        if (i >= sent_token_list.size())
        {
        //new token would reserve new memory, therefore,
        //we should check the buffer state of dest
                if (in_memory_remained <= 0)
                //if (0)
                {
                        return false;
                } else { //it consumes/resevers memory immediately, and need update when dst receive the pkt
                        assert(update_in_memory_write_pointer());
                        token_info_type temp;
                        temp.id = fl->get_tg_info().token_id;
                        temp.length_in_pkt = fl->get_tg_info().\
                        token_length_in_pkt;
                        temp.received_pkt = 1;
                        sent_token_list.push_back(temp);
                }
        } else {
                if (sent_token_list.at(i).length_in_pkt !=\
                                fl->get_tg_info().token_length_in_pkt){
                        fatal("error receiving token");
                        return false;
                }
                sent_token_list.at(i).received_pkt++;
        }
        //check token state
        if (sent_token_list.at(i).received_pkt == \
                sent_token_list.at(i).length_in_pkt)
        {
                sent_token_list.erase(sent_token_list.begin() + i);
                sent_token_list.shrink_to_fit();
                //at this moment, a buffer size is emptied
                assert(update_out_memory_read_pointer());
                /*
                if (src_task_id==0)
                        DPRINTF("task %d send pkt to task %d completely !\n", \
                        src_task_id, dst_task_id);
                */
        } else if (sent_token_list.at(i).received_pkt > \
                sent_token_list.at(i).length_in_pkt) {
                fatal("error receiving token");
                return false;
        }

        return true;
}

int
GraphEdge::get_random_token_size()
{
        int a = gen_normal_dist(mu_token_size, sigma_token_size);
        if (a > max_token_size)
                a = max_token_size;
        else if (a <= 0)
                a = 1;
        return a;
}

int
GraphEdge::set_statistical_token_size(double mu, double sigma)
{

        assert(mu > 0 && sigma >= 0);
        mu_token_size = mu;
        sigma_token_size = sigma;

        return 0;
}

int
GraphEdge::get_random_pkt_interval()
{

        double a = gen_exp_dis_time(lambda_pkt_interval);
        return a;
}

int
GraphEdge::set_statistical_pkt_interval(double lambda)
{

        assert(lambda > 0);
        lambda_pkt_interval = lambda;

        return 0;
}

int GraphEdge::get_id() { return id; }

int
GraphEdge::set_id(int eid)
{
        assert(eid >= 0);
        id = eid;
        return 0;
}

int GraphEdge::get_src_task_id() { return src_task_id; }

int
GraphEdge::set_src_task_id(int tid)
{
        assert(tid >= 0);
        src_task_id = tid;
        return 0;
}

int GraphEdge::get_dst_task_id() { return dst_task_id; }

int
GraphEdge::set_dst_task_id(int tid)
{
        assert(tid >= 0);
        dst_task_id = tid;
        return 0;
}

int GraphEdge::get_src_proc_id() { return src_proc_id; }

int
GraphEdge::set_src_proc_id(int pid)
{
        assert(pid >= 0);
        src_proc_id = pid;
        return 0;
}

int GraphEdge::get_dst_proc_id() { return dst_proc_id; }

int
GraphEdge::set_dst_proc_id(int pid)
{
        assert(pid >= 0);
        dst_proc_id = pid;
        return 0;
}

// Set in GarnetNetwork
int GraphEdge::set_vc_choice(int vid) 
{ 
        assert(vid >= 0);
        vc_choice = vid;
        return 0; 
}
// Return vc_choice for NI
int GraphEdge::get_vc_choice() { return vc_choice; }

int GraphEdge::get_max_token_size() { return max_token_size; }

int
GraphEdge::set_max_token_size(int size)
{
        assert(size > 0);
        max_token_size = size;
        return 0;
}
