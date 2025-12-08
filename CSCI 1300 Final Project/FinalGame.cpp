#include <iostream>
#include <string>
#include "Board.cpp"
#include "OtherHeader.cpp"

using namespace std;

int main() {
    //initialize board & random seed
    Board BigB;
    srand(time(NULL));
    //choose characters
    CharacterSelection();
    Characters temp1(1, Character1, 0);
    Characters temp2(2, Character2, 1);
    BigB.p1 = temp1;
    BigB.p2 = temp2;

    system ("pause");

    //choose path
    BigB.p1.PathSelection(BigB.p1.number);
    if (BigB.p1.path == true) {
        BigB.p1.AdvisorSelection(BigB.p1.number);
    }

    system("pause");

    BigB.p2.PathSelection(BigB.p2.number);
    if (BigB.p2.path == true) {
        BigB.p2.AdvisorSelection(BigB.p2.number);
    }

    system("pause");

    cout << "The game will now begin!" << endl;

    system("pause");

    BigB.displayBoard();
    BigB.p1.PrintStats(2);
    BigB.p2.PrintStats(2);

    
    
    return(0);
}