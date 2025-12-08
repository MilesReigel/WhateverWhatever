// Recognized as "include guards"
// Prevent the board header file from being used more than once
#ifndef BOARD_H
#define BOARD_H

#include <string>
#include "Tile.h"
using std::string;

int p1c = 0;
int p2c = 1;

int Character1 = 0, Character2 = 0;
int statMinimum = 100;
int second = 1000;

class Characters { 
public:
    Characters();
    Characters(int player, int character, int index);
    void PathSelection(int player);
    void PrintStats(int typeOfCall);
    void AdvisorSelection(int player);    

    std::string name;
    int Dsp, Exp, Acc, Eff, Ins, number, advisor, index;
    bool path, theft, trapAhead;
};

class Board {
    private:
        // Static in this context: Belongs to the class, not each object
        static const int _BOARD_SIZE = 52;
        static const int _MAX_PLAYERS = 2;

        // Composition!
        Tile _tiles[2][_BOARD_SIZE];

        int _player_count;
        int _player_position[_MAX_PLAYERS];

        void initializeTiles(int player_index);
        bool isPlayerOnTile(int player_index, int pos);
        void displayTile(int player_index, int pos);

    public:
        // Default Constructor
        Board();    

        Characters p1, p2;

        void initializeBoard();
        void displayTrack(int player_index);
        void displayBoard();
        bool movePlayer(int player_index);
        // Recall we can use const for getter functions
        int getPlayerPosition(int player_index) const;
        void turn(int player_index);
        int RollDice();
        void misfortune(int player); // this
        void events(int player); // this
        void DspAddition(int player, int amount); // this
};

#endif