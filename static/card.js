console.log(typeof cards_json);


console.log(cards_json);

var num_cards = cards_json["num_cards"];
var card_index = 0;

var num_correct = 0;
var num_incorrect = 0;

var angle = 0;
var is_animating = false;
var flipped = false;

var card_container  = document.getElementById("card-container");
var card_next       = document.getElementById("card-next");
var card_front      = document.getElementById("card-front");
var card_back       = document.getElementById("card-back");
var stack_correct   = document.getElementById("stack-correct");
var stack_incorrect = document.getElementById("stack-incorrect")

function shuffle(array) {
    for (let i = array.length - 1; i >= 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
}

shuffle(cards_json["cards"])
initCards();

function getScreenPos(element) {
    var rect = element.getBoundingClientRect();
    return [rect.left, rect.top];
}

function rotateY(element, angle) {
    element.style.transform = "rotateY(" + angle + "deg)";
}

function setTransitionTime(element, time) {
    element.style.transition = "all " + time + "s ease-in-out";
}

function glide(element, x, y) {
    element.style.left = x + "px";
    element.style.top = y + "px";
}

function glideTo(element, target_element) {
    const [correct_x, correct_y] = getScreenPos(target_element);
    const [card_x, card_y] = getScreenPos(element);
    var dest_x = correct_x - card_x;
    var dest_y = correct_y - card_y;
    glide(element, dest_x, dest_y);
}

function getSize(element) {
    var rect = element.getBoundingClientRect();
    return [rect.right - rect.left, rect.bottom - rect.top];
}

function setSize(element, width, height) {
    element.style.width = width + "px";
    element.style.height = height + "px";
}

function setFontSize(element, size) {
    element.style.fontSize = size + "rem";
}

function flipCard() {
    if (is_animating) return;
    flipped = !flipped;
    is_animating = true;
    setTransitionTime(card_front, 1.0);
    setTransitionTime(card_back, 1.0);
    angle = (angle + 180) % 360;
    rotateY(card_front, angle);
    rotateY(card_back, angle + 180);
    setTimeout(function() {
        is_animating = false;
    }, 1000);
}

function resetCard(card) {
    setTransitionTime(card, 0.0);
    card.style.top = "0px";
    card.style.left = "0px";
    card.style.width = "100%";
    card.style.height = "100%";
    card.style.fontSize = "1rem";
    if (flipped) {
        angle = (angle + 180) % 360;
        rotateY(card_front, angle);
        rotateY(card_back, angle + 180);
        flipped = !flipped;
    }
}

function resetCards() {
    resetCard(card_front);
    resetCard(card_back);
}

function zoomNextCard() {
    setTransitionTime(card_next, 1.0);
    card_next.style.width = "100%";
    card_next.style.height = "100%";
    setFontSize(card_next, 1);
    setTimeout(function() {
        setTransitionTime(card_next, 0);
        card_next.style.width = "80%";
        card_next.style.height = "80%";
        setFontSize(card_next, 0.8);
    }, 1000);
}

function moveCardToStack(card, stack, time) {
    const [stack_width, stack_height] = getSize(stack);
    const [card_width, card_height] = getSize(card_container);
    var font_size = stack_height / card_height

    setTransitionTime(card, time);
    glideTo(card, stack);
    setSize(card, stack_width, stack_height);
    setFontSize(card, font_size);
}

function moveCardsToStack(stack, stack_height) {
    is_animating = true;
    incrementCount("attemps");
    moveCardToStack(card_front, stack, 1.0);
    moveCardToStack(card_back, stack, 1.0);
    zoomNextCard();
    setTimeout(function() {
        is_animating = false;
        updateCards(stack);
        resetCards();
        updateShadow(stack, stack_height);
        if (stack_height == 1) {
            stack.style.border = "0px solid #000000";
        }
    }, 1000);
}

function updateShadow(stack, size) {
    if (size > 10) {
        size = 10;
    }
    stack.style.boxShadow = size + "px " + size + "px 10px #000000";
}

function removeStackBorder (stack) {
    stack.style.removeProperty("border");
}

function updateNextCard() {
    var next_index = card_index + 1;
    if (next_index >= num_cards) {
        card_next.innerHTML = "";
        card_next.style.removeProperty("background-color");
    } else {
        card_next.innerHTML = cards_json["cards"][next_index]["front"];

        var card_front_color = cards_json["cards"][card_index]["front_color"];
        if (card_front_color == "") {
            card_front_color = front_color;
        }
        card_next.style.backgroundColor = card_front_color;
    }
}

function initCards() {
    setTransitionTime(card_front, 0);
    setTransitionTime(card_back, 0);
    updateNextCard();
    card_front.innerHTML = cards_json["cards"][card_index]["front"];
    card_back.innerHTML = cards_json["cards"][card_index]["back"];

    var card_front_color = cards_json["cards"][card_index]["front_color"];
    if (card_front_color == "") {
        card_front_color = front_color;
    }

    var card_back_color = cards_json["cards"][card_index]["back_color"];
    if (card_back_color == "") {
        card_back_color = back_color;
    }

    card_front.style.backgroundColor = card_front_color;
    card_back.style.backgroundColor = card_back_color;
}

function clearCards() {
    setTransitionTime(card_front, 0);
    setTransitionTime(card_back, 0);
    setTransitionTime(card_next, 0);
    card_front.innerText = "";
    card_back.innerText = "";
    card_next.innerText = "Quiz complete!";
    card_front.style.removeProperty("background-color");
    card_back.style.removeProperty("background-color");
    card_next.style.removeProperty("background-color");
}

function incrementCount(count_key) {
    var current_count_str = cards_json["cards"][card_index][count_key];
    var current_count = 0;
    if (typeof current_count_str === 'string' || current_count_str instanceof String) {
        current_count = parseInt(current_count_str);
    } else {
        current_count = current_count_str;
    }
    current_count += 1;
    cards_json["cards"][card_index][count_key] = current_count;
}

function postResults() {
    var fetch_url = "/card_update/" + cards_json["uuid"];
    fetch(fetch_url, {
        method: "POST",
        body: JSON.stringify(cards_json),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    });
}

function updateCards(stack) {
    card_index += 1;
    setTransitionTime(card_front, 0);
    setTransitionTime(card_back, 0);
    stack.innerText = card_back.innerText;
    stack.style.backgroundColor = card_back.style.backgroundColor;
    stack.style.fontSize = card_back.style.fontSize;
    if (card_index < num_cards) {
        initCards();
    } else {
        clearCards();
        postResults();
    }
}

function allowAnimation() {
    return (flipped && !is_animating) && (card_index < num_cards);
}

card_container.onclick = flipCard;

stack_correct.onclick = function() {
    if (!allowAnimation()) return;
    num_correct += 1;
    incrementCount("correct");
    moveCardsToStack(stack_correct, num_correct);
}

stack_incorrect.onclick = function() {
    if (!allowAnimation()) return;
    num_incorrect += 1;
    moveCardsToStack(stack_incorrect, num_incorrect);
}
