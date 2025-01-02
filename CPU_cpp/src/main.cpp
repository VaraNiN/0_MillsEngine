#include "Engine.h"
#include "GUI.h"
#include "Utilities.h"
#include "UserInput.h"
#include <iostream>
#include <bitset>

int main() {
    BoardState state;   //Current board position
    History history;    //History of all board positions
    history.saveState(state);

    std::vector<BoardState> children;

    inputAdd(state, history);
    inputAdd(state, history);
    inputAdd(state, history);
    inputAdd(state, history);
    inputAdd(state, history);
    inputAdd(state, history);
    state.moveNumber = 20;
    checkPhase(state);
    children = getChildren(state);

    for (BoardState child : children) {
        show_position(child);
        print(child);
    }
    show_position(state);
    print(state);

    inputAdd(state, history);
    inputAdd(state, history);
    checkPhase(state);
    children = getChildren(state);
    
    for (BoardState child : children) {
        show_position(child);
        print(child);
    }
    show_position(state);
    print(state);


    //state.whitePieces = generateRandomBitset();
    //state.blackPieces = generateRandomBitset();
    //timeStuff(state);

    return 0;
}