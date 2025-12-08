#include "Board.h"
#include <cstdlib>
#include <ctime>
#include <iostream>
#include "OtherHeader.cpp"


// Each of the following defines a macro
// Essentially nicenames to use instead of the corresponding escape sequence ('\') 
#define ORANGE "\033[48;2;230;115;0m"
#define GREY "\033[48;2;128;128;128m"
#define GREEN "\033[48;2;34;139;34m"
#define BLUE "\033[48;2;10;10;230m"
#define PINK "\033[48;2;255;105;180m"
#define BROWN "\033[48;2;139;69;19m"
#define RED "\033[48;2;230;10;10m"
#define PURPLE "\033[48;2;128;0;128m"
#define RESET "\033[0m"

using namespace std;

// =========================== Constructor ===========================

Board::Board() {
    // Creates two players
    _player_count = _MAX_PLAYERS;

    // Initialize player's position
    for (int i = 0; i < _player_count; i++) {
        _player_position[i] = 0;
    }

    // Fill both lanes
    initializeBoard();
}

// =========================== Private Member Functions ===========================

void Board::initializeTiles(int player_index) {
    Tile tile;
    int green_count = 0;
    // Recall 52 from header file
    int total_tiles = _BOARD_SIZE;

    for (int i = 0; i < total_tiles; i++) {
        // Set the last tile as Orange for the finish line
        if (i == total_tiles - 1) {
            tile.color = 'O';
        } 
        // Set the first tile as Grey for the starting line
        else if (i == 0) {
            tile.color = 'Y';
        } 
        // Hard-coded target of 30 green tiles
        // Probablisitic method to spread out the green tiles randomly
        else if (green_count < 30 && (rand() % (total_tiles - i) < 30 - green_count)) {
            tile.color = 'G';
            green_count++;
        }
        // Randomly assign one of the other colors: Blue, Pink, Brown, Red, Purple
        else {
            int color_choice = rand() % 5;
            switch (color_choice) {
                case 0:
                    tile.color = 'B'; // Blue
                    break;
                case 1:
                    tile.color = 'P'; // Pink
                    break;
                case 2:
                    tile.color = 'T'; // Brown
                    break;
                case 3:
                    tile.color = 'R'; // Red
                    break;
                case 4:
                    tile.color = 'U'; // Purple
                    break;
            }
        }

        // Assign the tile to the board for the specified lane/player 1 or 2
        // Recall i refers to tile 0 to 51
        _tiles[player_index][i] = tile;
    }
}

bool Board::isPlayerOnTile(int player_index, int pos) {
    if (_player_position[player_index] == pos) {
        return true;
    }
    return false;
}

void Board::displayTile(int player_index, int pos) {
    string color = "";
    int player = isPlayerOnTile(player_index, pos);

    // Using the defined nicenames above
    switch(_tiles[player_index][pos].color) {
        case 'O': color = ORANGE; break;
        case 'Y': color = GREY; break;
        case 'G': color = GREEN; break;
        case 'B': color = BLUE; break;
        case 'P': color = PINK; break;
        case 'T': color = BROWN; break;
        case 'R': color = RED; break;
        case 'U': color = PURPLE; break;
    }

    // Template for displaying a tile: <line filler space> <color start> |<player symbol or blank space>| <reset color> <line filler space> <endl>
    if (player == true) {
        cout << color << "|" << (player_index + 1) << "|" << RESET;
    }
    else {
        cout << color << "| |" << RESET;
    }
}

// =========================== Public Member Functions ===========================

void Board::initializeBoard() {
    for (int i = 0; i < 2; i++) {
        // This ensures each lane (or each player) has a unique tile distribution
        initializeTiles(i);
    }
}

void Board::displayTrack(int player_index) {
    for (int i = 0; i < _BOARD_SIZE; i++) {
        displayTile(player_index, i);
    }
    cout << endl;
}

void Board::displayBoard() {
    for (int i = 0; i < 2; i++) {
        displayTrack(i);
        if (i == 0) {
            cout << endl; // Add an extra line between the two lanes
        }
    }
}

bool Board::movePlayer(int player_index) {
    // Increment player position by 1
    _player_position[player_index]++;

    if (((rand() % 4) == 2) && (_player_position[player_index] != (_BOARD_SIZE - 1))) {
        misfortune(player_index + 1);
    }

    // Player reached last tile
    if (_player_position[player_index] == _BOARD_SIZE - 1) {
        return true;
    }

    return false;
}

int Board::getPlayerPosition(int player_index) const {
    if (player_index >= 0 && player_index <= _player_count) {
        return _player_position[player_index];
    }
    return -1;
}

int Board::RollDice() {
    int roll = (rand() % 6) + 1 ;
    return(roll);
}

void Board::turn(int player) {
    Characters &active = (player == 1) ? p1 : p2;

    int choice, roll;
    cout << endl << "It is player " << player << "'s turn! choose one of the options below: " << endl;
    cout << "1: Roll your dice to move forward" << endl;
    cout << "2: Check your character stats" << endl;
    cout << "3: View Board" << endl;
    cout << "4: Attempt to sabotage the other player" << endl;
    cout << "5: Gamble?" << endl << endl;
    cout << "Enter your choice: ";
    cin >> choice;
    switch (choice) {
        case 1:
            roll = RollDice();
            cout << endl << "Player " << player << " has rolled!" << endl;
            cout << "Rolling..." << endl;
            if ((rand() % 20) == 6) {
                cout << "(\"That's not what it does\")" << endl;
            }
            // Sleep(second);
            if (active.trapAhead) {
                roll -= 1;
                cout << "The glue is sticky! You rolled a " << roll + 1 << " but you got a little stuck" << endl;
                cout << "You only move " << roll << " tiles." << endl;
                if (roll == 0) {cout << "(0 tiles? Are you kidding me? You must have really gotten stuck there.)" << endl;}
                cout << endl;
            }
            else {
                cout << "Player " << player << " has rolled a " << roll << endl << endl;
            }
            for (int i = 0; i < roll; i++) {
                if(movePlayer(player - 1)) {
                    Victory(player - 1);
                }
            }
            displayBoard();
            break;
        case 2:
            cout << "Would you like to see Experience and Advisor(1) or Discovery Points and other stats(2)? " << endl;
            cin >> choice;
            if (choice == 1) {
                active.PrintStats(1);
            }
            else if (choice == 2) {
                active.PrintStats(2);
            }
            else {
                cout << "That wasn't an option you goof" << endl;
            }
            turn(player);
            break;
        case 3:
            displayBoard();
            turn(player);
            break;
        case 4:
            cout << "You have two options for your naerdowelling - you can either trap the path with Elmer's school glue and" << endl;
            cout << "subtract one tile from you ropponent's next roll (type 1, with a 2 in 3 chance of success) " << endl;
            cout << "or curse their next Discovery Point gain and take half of it for yourself (type 2, with a 1 in 2 chance of success): " << endl;
            cin >> choice;
            // trap
            if (choice == 1) {
                cout << "You attempt to trap the path..." << endl;
                // Sleep(second);
                //fail
                if ((rand() % 3) == 1) {
                    cout << "They caught on to your trickery and know about the trap. Better luck next time." << endl;
                }
                //succeed
                else {
                    cout << "Your oppenent will surely be slowed down on their next roll." << endl;
                    if (p1.name == active.name) {
                        p2.trapAhead = true;
                        cout << "p2.trap set" << endl;
                    }
                    else {
                        p1.trapAhead = true;
                        cout << "p1.trap set" << endl;
                    }
                }
            }
            //theft
            else if (choice == 2) {
                //fail
                if ((rand() % 2) == 0) {
                    cout << "The FBDPI (Federal Bureau of Discovery Point Investigation) sees your search history:" << endl;
                    cout << "\"How to sabotage DP gain and take half of it for myself reddit\"" << endl << "\"How to ";
                    cout << "steal someone else's discovery points easy tutorial \"" << endl << "You are on a watch list ";
                    cout << "now. Maybe try searching with DuckDuckGo next time" << endl;
                }
                //succeed
                else {
                    cout << "You figure out how to take advantage of their work for your own gain. Effective? Yes." << endl;
                    cout << "Morally wrong? Certainly. But clearly you don't care." << endl;
                    cout << "Half of player ";
                    if (player == 1) {
                        cout << "2's ";
                    }
                    else {
                        cout << "1's ";
                    }
                    cout << "next Discovery Point gain will go to you." << endl;
                    active.theft = true;
                }
            }
            break;
        case 5:
            cout << "Let's go gambling!" << endl;
            cout << "This will cost you your turn. You have a 50/50 shot of earning or losing Discovery Points" << endl;
            cout << "To follow the storyline here, let's say you're just trying random genetic mutations in your" << endl;
            cout << "desperation to no longer be a failure. Are you sure you would like to proceed? (1 - yes, 2 - menu)" << endl;
            cin >> choice;
            // not gamble
            if (choice == 2) {
                cout << "The number one mistake new gamblers make is quitting before they win big. Remember that." << endl;
                turn(player);
            }
            //gamble
            else if (choice == 1) {
                cout << "You made the right choice." << endl;
                system("pause");
                cout << "Let's see if luck is on your side." << endl;
                system("pause");
                cout << "A pause for dramatic effect... " << endl;
                // Sleep(second * 3);
                if ((rand() % 2) == 1) {
                    cout << "You won! You actually won! I never thought that would happen." << endl;
                    cout << "+1000 Discovery Points!" << endl;
                    DspAddition(player, 1000);
                }
                else {
                    cout << "Aw dangit! You were so close. I'm sure you'll win next time though." << endl;
                    cout << "-1000 Discovery Points" << endl;
                    active.Dsp -= 1000;
                }
            }
            break;
        default:
            cout << "Invalid input, try that sh*t again chief" << endl;
            // turn(player, character);
    }
}

void Board::events(int player) {
    Characters &active = (player == 1) ? p1 : p2;

    int eventnum = rand() % 48;
    fstream EventsFile("events.txt");
    if (EventsFile.fail()) {
        cout << "File failed to open" << endl;
        exit(-1);
    }
    string event[4], line;
    int linecounter = 0;

    while (getline(EventsFile, line)) {
        int length = line.length(), barcounter = 0;
        if (linecounter == eventnum) {
            for (int i = 0; i < length; i++) {
                if (line[i] == '\r') continue;

                if (line[i] == '|') {
                    barcounter++;
                }
                else {
                    event[barcounter] = event[barcounter].append(line.substr(i, 1));
                }
            }
        }
        linecounter++;
    }

    cout << event[0] << "." << endl;
    if ((event[1] == "0") && (event[2] != "0") && (active.advisor == stoi(event[2]))) {
        cout << "Your advisor has saved you from misfortune! Your Discovery Points live to see" << endl;
        cout << "another day." << endl;
    }
    else {
        if (stoi(event[3]) > 0) {
            cout << "This is fortunate. + " << event[3] << " Discovery Points" << endl;
            DspAddition(player, stoi(event[3]));
        }
        else {
            cout << "This is unfortunate. Better luck next time! " << endl;
            cout << event[3] << " Discovery Points" << endl;
            active.Dsp += stoi(event[3]);
        }
    }
}

void Board::misfortune(int player) {
    Characters &active = (player == 1) ? p1 : p2;
    cout << "A surprise event has struck player " << player << "!" << endl;
    //riddle
    if ((rand() % 2) == 1) {
        string answer;
        cout << "player " << player << " must solve a riddle: " << endl << endl;
        int lineSelection = rand() % 25;
        cout << riddles(lineSelection, true) << endl;
        cin >> answer;
        if (riddles(lineSelection, false) == answer) {
            cout << "Wowie, you got it! That question was pretty easy though." << endl << "+500 Discovery Points" << endl;
            DspAddition(player, 500);
        }
        else {
            cout << "Haha I bet you wish that were the answer! It's actually " << riddles(lineSelection, false) << endl;
            cout << "You failed so badly that you get a penalty!" << endl;
            cout << "-500 Discovery Points for not paying more attention in class" << endl;
            active.Dsp -= 500;
        }
    }
    //event
    else {
        events(player);
    }
}

void Board::DspAddition(int player, int amount){
    if (p1.theft && player == 2) {
        cout << "Your sworn enemy has managed to steal half of your beautiful Discovery Point earnings!" << endl;
        p1.Dsp += amount/2;
        p2.Dsp += amount/2;
        p1.theft = false;
    }
    else if (p2.theft && player == 1) {
        cout << "Your sworn enemy has managed to steal half of your beautiful Discovery Point earnings!" << endl;
        p1.Dsp += amount/2;
        p2.Dsp += amount/2;
        p2.theft = false;
    }
    else {
        if (player == 1) {
            p1.Dsp += amount;
        }
        else {
            p2.Dsp += amount;
        }
    }
}

void Board::Victory(int player_index) {
    int player = player_index + 1;
    Characters &active = (player == 1) ? p1 : p2;
    Characters &opponent = (player == 1) ? p2 : p1;
    active.finished = true;
    cout << "Player " << player << " has completed the game!" << endl;
    if (active.finished && opponent.finished) {
        cout << "Both Players have completed the game!" << endl;
    }
    else if (active.finished && !opponent.finished) {
        cout << "Player " << player << " has won! Congratulations. Player " << opponent.index + 1 << " must now complete the game." << endl;
    }
    exit(0);
}