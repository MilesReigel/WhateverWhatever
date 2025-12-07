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
    Characters p1(1, Character1);
    Characters p2(2, Character2);

    system ("pause");

    //choose path
    p1.PathSelection(p1.number);
    if (p1.path == true) {
        p1.AdvisorSelection(p1.number);
    }

    system("pause");

    p2.PathSelection(p2.number);
    if (p2.path == true) {
        p2.AdvisorSelection(p2.number);
    }

    system("pause");

    cout << "The game will now begin!" << endl;

    system("pause");

    BigB.displayBoard();
    
    return(0);
}