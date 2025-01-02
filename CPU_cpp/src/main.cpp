#include "Engine.h"
#include "GUI.h"
#include "Utilities.h"
#include "UserInput.h"
#include <iostream>
#include <bitset>
#include <random>
#include <chrono>

int main() {
    BoardState state;   //Current board position
    History history;    //History of all board positions
    history.saveState(state);

    inputAdd(state, history);
    inputAdd(state, history);
    inputMove(state, history);
    inputRemove(state, history);

    return 0;
}