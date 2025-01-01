#ifndef GUI_H
#define GUI_H

#include <SFML/Graphics.hpp>
#include <vector>
#include <map>
#include <bitset>
#include <tuple>
#include "Engine.h"

void show_position(const BoardState& state, bool replace_symbols = true);

std::vector<int> runMillsBoard(BoardState& state, int inputs = 2);
std::map<int, sf::Vector2f> getVertices(int offset = -50);
int getVicinity(int x, int y, int offset = -50, int radius = 20);
void createMillsBoard(sf::RenderWindow& window, const BoardState& state, int width = 600, int height = 600, int offset = -50, int radius = 20);

#endif // GUI_H