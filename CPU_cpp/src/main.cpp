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

    while (true) {
        inputAdd(state, history);
        checkValidity(state);
        BoardState teststate;
        teststate.whitePieces = state.emptySpaces;
        show_position(teststate);
        inputAdd(state, history);
        checkValidity(state);
        teststate = BoardState();
        teststate.whitePieces = state.emptySpaces;
        show_position(teststate);
        inputMove(state, history);
        checkValidity(state);
        teststate = BoardState();
        teststate.whitePieces = state.emptySpaces;
        show_position(teststate);
        inputRemove(state, history);
        checkValidity(state);
        teststate = BoardState();
        teststate.whitePieces = state.emptySpaces;
        show_position(teststate);
    }

    return 0;
}