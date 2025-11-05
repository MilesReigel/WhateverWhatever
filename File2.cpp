#include <iostream>
#include <string>
#include <fstream>
#include <iomanip>
#include <cmath>

using namespace std;

struct Student {
    string name;
    int score;
};

void saveAndLoad() {
    Student s1;

    cout << "Initialize s1 name and score" << endl;
    cin >> s1.name >> s1.score;

    ofstream outFile("Student.txt");
    
    outFile << s1.name << " " << s1.score << endl;
    outFile.close();

    ifstream inFile("Student.txt");

    if (!inFile) {
        cout << "Failed to open file" << endl;
    }

    Student s2;
    inFile >> s2.name >> s2.score;
    inFile.close();
}

int main()
{
    saveAndLoad();

    return(0);
}