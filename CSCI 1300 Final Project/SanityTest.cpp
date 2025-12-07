#include <iostream>
#include <string>
#include "Board.cpp"
#include "OtherHeader.cpp"

using namespace std;

int main() {
    Board BigB;
    srand(time(NULL));

    Characters testP(1, 1);

    testP.advisor = 2;
    testP.path = 1;
    testP.PrintStats(1);

    testP.misfortune(1);
}