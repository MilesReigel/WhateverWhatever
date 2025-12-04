#include <iostream>
#include <string>
#include <fstream>
#include <iomanip>
<<<<<<< HEAD
using namespace std;

struct Restaurant {
public:    
    string name;
    int food_quality, cleanliness, wait_time;
    double overall;
};

double getOverallRating(Restaurant r){
    if (r.food_quality < 0 || r.food_quality > 10 || r.cleanliness < 0 || r.cleanliness > 10 || r.wait_time < 0 || r.wait_time > 10) {
        return(-1);
    }
    return((0.5 * r.food_quality) + (0.3 * r.cleanliness) + (0.2 * r.wait_time));
}

int readRestaurantDetails(string fname, Restaurant restaurant[], const int max_restaurants) {
    int linecounter = 0;
    ifstream file(fname);
    if (!file.is_open()) {
        return(-1);
    }

    string line;
    while (getline(file, line)) {
        int pos1 = 0, pos2 = 0, pos3 = 0, counter = 0, i = 0;
        for (char c : line) {
            if (c == '~') {
                counter++;
                switch (counter) {
                    case 1:
                        pos1 = i;
                        break;
                    case 2:
                        pos2 = i;
                        break;
                    case 3:
                        pos3 = i;
                }
            }
            i++;
        }
        restaurant[linecounter].name = line.substr(0, pos1);
        restaurant[linecounter].food_quality = stoi(line.substr(pos1 + 1, pos2 - pos1));
        restaurant[linecounter].cleanliness = stoi(line.substr(pos2 + 1, pos3 - pos2));
        restaurant[linecounter].wait_time = stoi(line.substr(pos3 + 1));
        restaurant[linecounter].overall = getOverallRating(restaurant[linecounter]);
        linecounter++;
    }
    return(linecounter);
}
=======
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
>>>>>>> 20cd6f6ea6edf82c02724dbfe1a2e43f8e240200

int getBest(Restaurant restaurants[], int size, string metric) {
    int bestMetric = 0, restaurant;
    if (metric == "Food Quality") {
        for (int i = 0; i < size; i++) {
            if (restaurants[i].food_quality > bestMetric) {
                bestMetric = restaurants[i].food_quality;
                restaurant = i;
            }
        }
    }
    else if (metric == "Cleanliness") {
        for (int i = 0; i < size; i++) {
            if (restaurants[i].cleanliness > bestMetric) {
                bestMetric = restaurants[i].cleanliness;
                restaurant = i;
            }
        }
    }
    else if (metric == "Wait Time") {
        for (int i = 0; i < size; i++) {
            if (restaurants[i].wait_time > bestMetric) {
                bestMetric = restaurants[i].wait_time;
                restaurant = i;
            }
        }
    }
    else if (metric == "Overall") {
        for (int i = 0; i < size; i++) {
            if (restaurants[i].overall > bestMetric) {
                bestMetric = restaurants[i].overall;
                restaurant = i;
            }
        }
    }
    else {
        return(-1);
    }
    return(restaurant);
}

int main() {
    cout << "Pizza the hut" << endl;
    Restaurant restaurants[30];
    int size = readRestaurantDetails("Budget.txt", restaurants, 30);
    if (size == -1) {
        cout << "Thats bad" << endl;
    }
    else if (size == 0) {
        cout << "Thats bad too lowk" << endl;
    }
    else {
        int idx = getBest(restaurants, size, "Overall");
        if (idx == -1){
            cout << "Dang cant do anything right" << endl;
        }
        else {
            cout << restaurants[idx].name << endl;
            cout << restaurants[idx].food_quality << " " << restaurants[idx].cleanliness << " " << restaurants[idx].wait_time << " " << restaurants[idx].overall << " ";
        }
    }
    return(0);
}