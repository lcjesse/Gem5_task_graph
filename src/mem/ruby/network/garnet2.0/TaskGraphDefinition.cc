#include "mem/ruby/network/garnet2.0/TaskGraphDefinition.hh"

static double tg_r_seed;
static double tg_seed = 91648253;

void
generate_seed()
{
    srand((unsigned)time(NULL));
    tg_r_seed=rand()%10;
        if (tg_r_seed==0)
                tg_r_seed=1;

}

double
tg_rnd()
{
        tg_r_seed=fmod(RAND_A*tg_r_seed,RAND_M);
        double k=tg_r_seed*4.656612875e-10;
        return(k);
}

double
tg_drand() {
        double &s = tg_seed;
        s *= 1389796;
        int q = (int)(s / 2147483647);
        s -= (double)q * 2147483647;
        return s / 2147483647;
}

double
gen_normal_dist(double m, double s) {

        double x1, x2, w, y1;
        static double y2;
        static int use_last = 0;

        if (use_last) {		        // use value from previous call
                y1 = y2;
                use_last = 0;
        }
        else {
                do {
                        x1 = 2.0 * tg_drand() - 1.0;
                        x2 = 2.0 * tg_drand() - 1.0;
                        w = x1 * x1 + x2 * x2;
                } while ( w >= 1.0 );

                w = sqrt( (-2.0 * log( w ) ) / w );
                y1 = x1 * w;
                y2 = x2 * w;
                use_last = 1;
        }

        return ( m + y1 * s );
}

double gen_exp_dis_time(double a) { return (-log(tg_rnd())/a); }
