#ifndef __MEM_RUBY_NETWORK_GARNET2_0_TASK_THREAD_HH__
#define __MEM_RUBY_NETWORK_GARNET2_0_TASK_THREAD_HH__

#include <iostream>
#include <vector>

#include "mem/ruby/network/garnet2.0/TaskThread.cc"
#include "mem/ruby/network/garnet2.0/CommonTypes.hh"

class TaskThread
{
  public:
    TaskThread(int id, int core_id, int core_idx) {}
    ~TaskThread() {}

  private:
    int m_id;
    int m_core_id;
    int m_core_idx;
    int m_app_idx;
    int m_task_id;
    int m_remained_execution_time;
    Thread_state m_thread_state;
};

#endif