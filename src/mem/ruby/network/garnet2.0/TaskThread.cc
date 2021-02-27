#include "mem/ruby/network/garnet2.0/TaskThread.hh"

TaskThread::TaskThread(int id, int core_id, int core_idx) {
    m_id = id;
    m_core_id = core_id;
    m_core_idx = core_idx;
    m_app_idx = -1;
    m_task_id = -1;
    m_remained_execution_time = -1;
    m_thread_state = _IDLE_;
}