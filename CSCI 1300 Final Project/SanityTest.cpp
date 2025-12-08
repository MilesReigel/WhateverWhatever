#include <iostream>
#include <string>
#include "Board.cpp"

using namespace std;

int main() {
    Board BigB;
    srand(time(NULL));

    //Sleep(rand() % 1000);

    Characters testP1(1, 1, 0);
    Characters testP2(2, 5, 1);

    BigB.p1 = testP1;
    BigB.p2 = testP2;

    BigB.p1.advisor = 2;
    BigB.p2.advisor = 0;
    BigB.p1.path = 1;
    BigB.p2.path = 0;
    BigB.p1.PrintStats(3);
    BigB.p2.PrintStats(3);

    BigB.misfortune(1);

    //test playloop
    while ((BigB.getPlayerPosition(p1c) < 52) || (BigB.getPlayerPosition(p2c) < 52)) {
        //if player 1 not finished
        if (BigB.getPlayerPosition(p1c) < 52) {
            BigB.turn(1);
        }
        BigB.p1.PrintStats(3);
        BigB.p2.PrintStats(3);
        //if player 2 not finished
        if (BigB.getPlayerPosition(p2c) < 52) {
            BigB.turn(2);
        }
        BigB.p2.PrintStats(3);
        BigB.p2.PrintStats(3);
    }

}