#include "GUI.h"
#include <iostream>
#include <vector>
#include <string>
#include <map>

// Simple ASCII Drawing of the board
void show_position(const BoardState& state, bool replace_symbols) {
    std::string board_template = R"(
        {0}-----------{1}-----------{2}
        |           |           |
        |   {3}-------{4}-------{5}   |
        |   |       |       |   |
        |   |   {6}---{7}---{8}   |   |
        |   |   |       |   |   |
        {9}---{10}---{11}       {12}---{13}---{14}
        |   |   |       |   |   |
        |   |   {15}---{16}---{17}   |   |
        |   |       |       |   |
        |   {18}-------{19}-------{20}   |
        |           |           |
        {21}-----------{22}-----------{23}
    )";

    std::vector<std::string> input(24);
    for (size_t i = 0; i < 24; ++i) {
        if (replace_symbols) {
            if (state.whitePieces[i]) {
                input[i] = "X"; // White piece
            } else if (state.blackPieces[i]) {
                input[i] = "O"; // White piece
            } else {
                input[i] = " ";
            }
        } else {
            input[i] = state.blackPieces[i] ? "1" : (state.whitePieces[i] ? "-1" : "0");
        }
    }

    for (size_t i = 0; i < input.size(); ++i) {
        std::string placeholder = "{" + std::to_string(i) + "}";
        size_t pos = board_template.find(placeholder);
        if (pos != std::string::npos) {
            board_template.replace(pos, placeholder.length(), input[i]);
        }
    }

    std::cout << board_template << std::endl;
}

// Function to get the vertices of the board
std::map<int, sf::Vector2f> getVertices(int offset) {
    return {
        {0, {40.0f, 40.0f - static_cast<float>(offset)}},
        {1, {300.0f, 40.0f - static_cast<float>(offset)}},
        {2, {560.0f, 40.0f - static_cast<float>(offset)}},
        {3, {120.0f, 120.0f - static_cast<float>(offset)}},
        {4, {300.0f, 120.0f - static_cast<float>(offset)}},
        {5, {480.0f, 120.0f - static_cast<float>(offset)}},
        {6, {200.0f, 200.0f - static_cast<float>(offset)}},
        {7, {300.0f, 200.0f - static_cast<float>(offset)}},
        {8, {400.0f, 200.0f - static_cast<float>(offset)}},
        {9, {40.0f, 300.0f - static_cast<float>(offset)}},
        {10, {120.0f, 300.0f - static_cast<float>(offset)}},
        {11, {200.0f, 300.0f - static_cast<float>(offset)}},
        {12, {400.0f, 300.0f - static_cast<float>(offset)}},
        {13, {480.0f, 300.0f - static_cast<float>(offset)}},
        {14, {560.0f, 300.0f - static_cast<float>(offset)}},
        {15, {200.0f, 400.0f - static_cast<float>(offset)}},
        {16, {300.0f, 400.0f - static_cast<float>(offset)}},
        {17, {400.0f, 400.0f - static_cast<float>(offset)}},
        {18, {120.0f, 480.0f - static_cast<float>(offset)}},
        {19, {300.0f, 480.0f - static_cast<float>(offset)}},
        {20, {480.0f, 480.0f - static_cast<float>(offset)}},
        {21, {40.0f, 560.0f - static_cast<float>(offset)}},
        {22, {300.0f, 560.0f - static_cast<float>(offset)}},
        {23, {560.0f, 560.0f - static_cast<float>(offset)}}
    };
}

// Function to get the vicinity of a click
int getVicinity(int x, int y, int offset, int radius) {
    auto vertices = getVertices(offset);
    for (const auto& [index, position] : vertices) {
        if ((position.x - radius <= x && x <= position.x + radius) &&
            (position.y - radius <= y && y <= position.y + radius)) {
            // Explicitly state which index is being returned
            std::cout << "Returning index: " << index << std::endl;
            return index;
        }
    }
    return -1;
}
// Function to create the Mills board
void createMillsBoard(sf::RenderWindow& window, const BoardState& state, int width, int height, int offset, int radius) {
    // Set the background color to light brown
    window.clear(sf::Color(210, 180, 140)); // Light brown

    sf::RectangleShape outerSquare(sf::Vector2f(static_cast<float>(width - 80), static_cast<float>(height - 80)));
    outerSquare.setPosition(40.0f, 40.0f - static_cast<float>(offset));
    outerSquare.setOutlineThickness(2.0f);
    outerSquare.setOutlineColor(sf::Color::Black); // Set line color to black
    outerSquare.setFillColor(sf::Color::Transparent);
    window.draw(outerSquare);

    sf::RectangleShape middleSquare(sf::Vector2f(static_cast<float>(width - 240), static_cast<float>(height - 240)));
    middleSquare.setPosition(120.0f, 120.0f - static_cast<float>(offset));
    middleSquare.setOutlineThickness(2.0f);
    middleSquare.setOutlineColor(sf::Color::Black); // Set line color to black
    middleSquare.setFillColor(sf::Color::Transparent);
    window.draw(middleSquare);

    sf::RectangleShape innerSquare(sf::Vector2f(static_cast<float>(width - 400), static_cast<float>(height - 400)));
    innerSquare.setPosition(200.0f, 200.0f - static_cast<float>(offset));
    innerSquare.setOutlineThickness(2.0f);
    innerSquare.setOutlineColor(sf::Color::Black); // Set line color to black
    innerSquare.setFillColor(sf::Color::Transparent);
    window.draw(innerSquare);

    sf::Vertex line1[] = {
        sf::Vertex(sf::Vector2f(static_cast<float>(width / 2), 40.0f - static_cast<float>(offset)), sf::Color::Black),
        sf::Vertex(sf::Vector2f(static_cast<float>(width / 2), 200.0f - static_cast<float>(offset)), sf::Color::Black)
    };
    window.draw(line1, 2, sf::Lines);

    sf::Vertex line2[] = {
        sf::Vertex(sf::Vector2f(static_cast<float>(width / 2), static_cast<float>(height - 40 - offset)), sf::Color::Black),
        sf::Vertex(sf::Vector2f(static_cast<float>(width / 2), static_cast<float>(height - 200 - offset)), sf::Color::Black)
    };
    window.draw(line2, 2, sf::Lines);

    sf::Vertex line3[] = {
        sf::Vertex(sf::Vector2f(40.0f, static_cast<float>(height / 2 - offset)), sf::Color::Black),
        sf::Vertex(sf::Vector2f(200.0f, static_cast<float>(height / 2 - offset)), sf::Color::Black)
    };
    window.draw(line3, 2, sf::Lines);

    sf::Vertex line4[] = {
        sf::Vertex(sf::Vector2f(static_cast<float>(width - 40), static_cast<float>(height / 2 - offset)), sf::Color::Black),
        sf::Vertex(sf::Vector2f(static_cast<float>(width - 200), static_cast<float>(height / 2 - offset)), sf::Color::Black)
    };
    window.draw(line4, 2, sf::Lines);

    auto vertices = getVertices(offset);
    for (const auto& [index, position] : vertices) {
        sf::CircleShape circle(static_cast<float>(radius));
        circle.setPosition(position.x - static_cast<float>(radius), position.y - static_cast<float>(radius));
        if (state.whitePieces.test(index)) {
            circle.setFillColor(sf::Color::White);
        } else if (state.blackPieces.test(index)) {
            circle.setFillColor(sf::Color::Black);
        } else {
            circle.setFillColor(sf::Color(139, 69, 19)); // Dark brown
        }
        window.draw(circle);
    }
}

// Function to run the Mills board application
std::vector<int> runMillsBoard(BoardState& state, int inputs) {
    sf::RenderWindow window(sf::VideoMode(600, 700), "Mills Board Click Tracker");
    std::vector<int> result;

    int fontsize = 20;

    // Create buttons
    sf::RectangleShape button1(sf::Vector2f(150, 50));
    button1.setPosition(50, 600);
    button1.setFillColor(sf::Color(230, 230, 250)); // Lavender

    sf::RectangleShape button2(sf::Vector2f(150, 50));
    button2.setPosition(225, 600);
    button2.setFillColor(sf::Color(75, 0, 130)); // Dark Purple (Indigo)

    sf::RectangleShape button3(sf::Vector2f(150, 50));
    button3.setPosition(400, 600);
    button3.setFillColor(sf::Color(139, 0, 0)); // Dark Red

    sf::Font font;
    if (!font.loadFromFile("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")) {
        std::cerr << "Failed to load font 'DejaVuSans.ttf'" << std::endl;
        return result;
    }

    sf::Text text1("Revert Half", font, fontsize);
    text1.setPosition(60, 610);
    text1.setFillColor(sf::Color::Black);

    sf::Text text2("Revert Full", font, fontsize);
    text2.setPosition(235, 610);
    text2.setFillColor(sf::Color::White);

    sf::Text text3("Abort Game", font, fontsize);
    text3.setPosition(410, 610);
    text3.setFillColor(sf::Color::White);

    while (window.isOpen()) {
        sf::Event event;
        while (window.pollEvent(event)) {
            if (event.type == sf::Event::Closed) {
                window.close();
            } else if (event.type == sf::Event::MouseButtonPressed) {
                if (event.mouseButton.button == sf::Mouse::Left) {
                    int x = event.mouseButton.x;
                    int y = event.mouseButton.y;

                    // Check if buttons are clicked
                    if (button1.getGlobalBounds().contains(x, y)) {
                        result.push_back(-1);
                        window.close();
                    } else if (button2.getGlobalBounds().contains(x, y)) {
                        result.push_back(-2);
                        window.close();
                    } else if (button3.getGlobalBounds().contains(x, y)) {
                        result.push_back(-3);
                        window.close();
                    } else {
                        int vicinity = getVicinity(x, y, 0, 20); // Adjust offset and radius as needed
                        if (vicinity != -1 && result.size() < inputs) {
                            result.push_back(vicinity);
                            if (result.size() == inputs) {
                                window.close();
                            }
                        }
                    }
                }
            }
        }

        window.clear(sf::Color(210, 180, 140)); // Set background color to light brown
        createMillsBoard(window, state, 600, 600, 0, 20); // Adjust width, height, offset, and radius as needed
        window.draw(button1);
        window.draw(button2);
        window.draw(button3);
        window.draw(text1);
        window.draw(text2);
        window.draw(text3);
        window.display();
    }

    return result;
}