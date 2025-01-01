#include "Engine.h"
#include "GUI.h"
#include "Utilities.h"

int main() {
    History history;
    BoardState state;

    history.saveState(state);

    state.whitePieces.set(5);
    state.blackPieces.set(6);

    history.saveState(state);

    // Accessing the history
    const auto& gameHistory = history.getHistory();
    for (const auto& state : gameHistory) {
        std::cout << generateKey(state) << std::endl;
        print(state);
    }

    return 0;


    int inputs = 24;
    std::vector<int> result = runMillsBoard(state, inputs);

    for (int index : result) {
        std::cout << "Clicked vicinity: " << index << "\n";
    }

    return 0;
}