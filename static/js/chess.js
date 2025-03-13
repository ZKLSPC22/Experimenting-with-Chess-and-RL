// Constants and Configurations
const pieceIcons = {
    'P': '♙', 'p': '♟',
    'R': '♖', 'r': '♜',
    'N': '♘', 'n': '♞',
    'B': '♗', 'b': '♝',
    'Q': '♕', 'q': '♛',
    'K': '♔', 'k': '♚'
};


// Game State Variables
let board = [];
let selectedSquare = null;
let selectedSquareElement = null;
let squares = [];
let botEnabled = null;
const botColor = bottomColor


// Coordinate Conversion Helpers, backend coordinates aligns with white pieces
function convertIndex(index, color) {
    return color === 'white' ? index : 63 - index;
}

function getCoordinatesFromIndex(index) {
    const row = Math.floor(index / 8);
    const col = index % 8;
    return [row, col];
}

function getIndexFromCoordinates(coords) {
    const [row, col] = coords;
    return row * 8 + col;
}


// Board Management
async function updateBoard() {
    console.log('Starting updateBoard function'); // Log when the function starts
    try {
        console.log('Fetching board data from /board'); // Log before fetching board data
        const response = await fetch('/board');
        console.log('Board data fetched, parsing JSON'); // Log after fetching, before parsing JSON
        const data = await response.json();
        console.log('Board data parsed:', data); // Log the parsed data
        console.log('Updating board variable'); // Log before updating the board variable
        board = data.board;
        console.log('Updating turnColor variable:', data.turn_color); // Log before updating turnColor
        turnColor = data.turn_color;
        console.log('Iterating over squares to update them'); // Log before iterating over squares
        squares.forEach((square, index) => {
            console.log('Processing square at index:', index); // Log the current square index
            index = convertIndex(index, bottomColor);
            console.log('Converted index:', index); // Log the converted index
            const [row, col] = getCoordinatesFromIndex(index);
            console.log('Coordinates for square:', { row, col }); // Log the coordinates
            const piece = board[row][col];
            console.log('Piece at coordinates:', piece); // Log the piece at the coordinates
            square.textContent = (piece && piece !== '.') 
                ? pieceIcons[piece] || piece 
                : '';
            console.log('Updated square text content:', square.textContent); // Log the updated text content
            square.style.color = piece && piece === piece.toLowerCase() 
                ? 'black' 
                : 'white';
            console.log('Updated square color:', square.style.color); // Log the updated color
        });
        console.log('Finished updating all squares'); // Log after all squares are updated
    } catch (error) {
        console.error('Error updating board:', error); // Log any errors
    }
    console.log('Finished updateBoard function'); // Log when the function ends
}

function initializeChessBoard() {
    const chessBoard = document.getElementById('chess-board');
    chessBoard.innerHTML = '';
    
    for (let i = 0; i < 64; i++) {
        const square = document.createElement('div');
        const isLight = (Math.floor(i / 8) + (i % 8)) % 2 === 0;
        square.className = `square ${isLight ? 'light' : 'dark'}`;
        square.id = `square-${i}`;
        chessBoard.appendChild(square);
    }

    squares = document.querySelectorAll('.square');
    squares.forEach(square => {
        square.addEventListener('click', handleSquareClick);
    });
}


// Game Logic
function getPieceAt(coords) {
    const [row, col] = coords;
    return board[row][col] && board[row][col] !== '.' ? board[row][col] : null;
}

function handleGameEnd(response) {
    if (response.game_over) {
        alert(response.message);
        squares.forEach(square => square.removeEventListener('click', handleSquareClick));
    }
}


// Move Handling & Visualization
async function highlightValidMoves(start) {
    try {
        const response = await fetch('/get_possible_moves', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ start: start })
        });
        const data = await response.json();
        console.log("Possible moves returned:", data.moves);
        data.moves.forEach(move => {
            let index = getIndexFromCoordinates(move);
            index = convertIndex(index, bottomColor);
            document.getElementById(`square-${index}`)?.classList.add('highlight');
        });
    } catch (error) {
        console.error('Error getting possible moves:', error);
    }
}

function clearSquareHighlights() {
    squares.forEach(square => {
        if (square !== selectedSquareElement) square.style.border = '';
        square.classList.remove('highlight');
    });
}

async function handleSquareClick(event) {
    let squareIndex = Array.from(squares).indexOf(event.target);
    if (squareIndex === -1) return;

    squareIndex = convertIndex(squareIndex, bottomColor);
    const coords = getCoordinatesFromIndex(squareIndex);

    if (!selectedSquare) {
        const piece = getPieceAt(coords);
        if (piece) {
            if (turnColor === 'white' && piece !== piece.toUpperCase()) return;
            if (turnColor === 'black' && piece !== piece.toLowerCase()) return;
            if (botEnabled != null) {
                if (bottomColor === 'white' && piece === piece.toLowerCase()) return;
                if (bottomColor === 'black' && piece === piece.toUpperCase()) return;
            }
            clearSquareHighlights();
            selectedSquare = coords;
            selectedSquareElement = event.target;
            event.target.style.border = '2px solid red';
            await highlightValidMoves(coords);
        }
    } else {
        const [start, end] = [selectedSquare, coords];
        clearSquareHighlights();
        selectedSquareElement.style.border = '';
        selectedSquare = null;
        selectedSquareElement = null;

        try {
            const response = await fetch('/move', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ start, end })
            });
            
            const data = await response.json();
            if (data.status === 'success') {
                console.log('handleSquareClick updateBoard');
                await updateBoard();
                handleGameEnd(data);
            } else {
                alert('Invalid move!');
                console.log('handleSquareClick updateBoard');
                await updateBoard();
            }
        } catch (error) {
            console.error('Move error:', error);
            console.log('handleSquareClick updateBoard');
            await updateBoard();
        }
    }
}

function clearSquareSelection() {
    if (selectedSquareElement) {
        selectedSquareElement.style.border = '';
    }
    selectedSquare = null;
    selectedSquareElement = null;
}


// UI Controls & Event Handlers
function setupBotToggle() {
    const botControls = document.getElementById('bot-controls');
    
    // Handle ALL checkbox changes in the container
    botControls.addEventListener('change', (e) => {
        if (!e.target.matches('input[type="checkbox"]')) return;
        
        const checkboxes = botControls.querySelectorAll('input[type="checkbox"]');
        const checkedBot = e.target.checked ? e.target.value : null;

        // Uncheck all others when a checkbox is checked
        if (e.target.checked) {
            checkboxes.forEach(checkbox => {
                if (checkbox !== e.target) checkbox.checked = false;
            });
        }
        
        // Your existing API call
        fetch('/bot-mode', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({bot_enabled: checkedBot})
        }).catch(console.error);
        console.log('setupBotToggle updateBoard');
        updateBoard();
    });
}

document.getElementById('restart-btn').addEventListener('click', () => {
    fetch('/restart', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            clearSquareHighlights();
            clearSquareSelection();
            const botToggleElem = document.getElementById('bot-controls'); // this gives null, why?
            botToggleElem.checked = false;
            botEnabled = null;
            bottomColor = data.bottom_color;
            console.log('restart-btn updateBoard');
            updateBoard();
        })
        .catch(error => console.error('Error restarting game:', error));
});


// Initialization
document.addEventListener('DOMContentLoaded', () => {
    initializeChessBoard();
    setupBotToggle();
    console.log('DOM updateBoard');
    updateBoard();
});
