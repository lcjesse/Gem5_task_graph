#ifndef __MEM_RUBY_NETWORK_GARNET2_0_TASK_GRAPH_dEFINITION_HH__
#define __MEM_RUBY_NETWORK_GARNET2_0_TASK_GRAPH_dEFINITION_HH__

#include <cmath>

#include "stdlib.h"
#include "time.h"

#define RAND_A 16807.0
#define RAND_M 2147483647.0

// generate double in (0, 1)
void generate_seed();

//generate uniform distribution random in(0,1)
// random is stored in r_seed
double tg_rnd();
double tg_drand();


// normal random variate generator
// mean m, standard deviation s
double gen_normal_dist(double m, double s);

//generate exponantial variable with parameter a
double gen_exp_dis_time(double a);

#endif