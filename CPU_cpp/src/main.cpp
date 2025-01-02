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
    children = getChildren(state);

    for (BoardState child : children) {
        show_position(child);
    }


    //state.whitePieces = generateRandomBitset();
    //state.blackPieces = generateRandomBitset();
    //timeStuff(state);

    return 0;
}