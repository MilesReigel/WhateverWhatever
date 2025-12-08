#include <iostream>
#include <string>
#include "Board.cpp"
#include "OtherHeader.cpp"

using namespace std;

int main() {
    Board Board;
    srand(time(NULL));

    Sleep(rand() % 1000);

    Characters testP1(1, 1);
    Characters testP2(2, 5);

    // change constructor settings to involve the creation of characters object under board

    testP1.advisor = 2;
    testP2.advisor = 0;
    testP1.path = 1;
    testP2.path = 0;
    testP1.PrintStats(1, 3);
    testP2.PrintStats(2, 3);

    testP1.misfortune(1, testP1, testP2);

    //test playloop
    while ((Board.getPlayerPosition(p1c) < 52) || (Board.getPlayerPosition(p2c) < 52)) {
        //if player 1 not finished
        if (Board.getPlayerPosition(p1c) < 52) {
            Board.turn(1, testP1, testP1, testP2);
        }
        testP1.PrintStats(1, 3);
        testP2.PrintStats(2, 3);
        //if player 2 not finished
        if (Board.getPlayerPosition(p2c) < 52) {
            Board.turn(2, testP2, testP1, testP2);
        }
        testP2.PrintStats(2, 3);
        testP1.PrintStats(1, 3);
    }

}