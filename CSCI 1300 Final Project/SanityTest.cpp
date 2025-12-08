#include <iostream>
#include <string>
#include "Board.cpp"
#include "OtherHeader.cpp"

using namespace std;

int main() {
    Board BigB;
    srand(time(NULL));

    Characters testP1(1, 1);
    Characters testP2(2, 5);

    testP1.advisor = 2;
    testP2.advisor = 0;
    testP1.path = 1;
    testP2.path = 0;
    testP1.PrintStats(1, 3);
    testP2.PrintStats(2, 3);

    testP1.misfortune(1, testP1, testP2);

    //test playloop
    while ((BigB.getPlayerPosition(p1c) < 52) || (BigB.getPlayerPosition(p2c) < 52)) {
        //if player 1 not finished
        if (BigB.getPlayerPosition(p1c) < 52) {
            BigB.turn(1, testP1, testP1, testP2);
        }
        //if player 2 not finished
        if (BigB.getPlayerPosition(p2c) < 52) {
            BigB.turn(2, testP2, testP1, testP2);
        }
    }

}