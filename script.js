const braille = {
    'а': [1, 0, 0, 0, 0, 0], 
    'б': [1, 0, 1, 0, 0, 0],
    'в': [0, 1, 1, 1, 0, 1],
    'г': [1, 1, 1, 1, 0, 0],
    'ґ': [1, 1, 1, 1, 0, 1],
    'д': [1, 1, 0, 1, 0, 0],
    'е': [1, 0, 0, 1, 0, 0],
    'є': [0, 1, 0, 1, 1, 0],
    'ж': [0, 1, 1, 1, 0, 0],
    'з': [1, 0, 0, 1, 1, 1],
    'и': [0, 1, 1, 0, 0, 0],
    'і': [1, 1, 0, 1, 1, 1],
    'ї': [1, 1, 0, 1, 0, 1],
    'й': [1, 1, 1, 0, 1, 1],
    'к': [1, 0, 0, 0, 1, 0],
    'л': [1, 0, 1, 0, 1, 0],
    'м': [1, 1, 0, 0, 1, 0],
    'н': [1, 1, 0, 1, 1, 0],
    'о': [1, 0, 0, 1, 1, 0],
    'п': [1, 1, 1, 0, 1, 0],
    'р': [1, 0, 1, 1, 1, 0],
    'с': [0, 1, 1, 0, 1, 0],
    'т': [0, 1, 1, 1, 1, 0],
    'у': [1, 0, 0, 0, 1, 1],
    'ф': [1, 1, 1, 0, 0, 0],
    'х': [1, 0, 1, 1, 0, 0],
    'ц': [1, 1, 0, 0, 0, 0],
    'ч': [1, 1, 1, 1, 1, 0],
    'ш': [1, 0, 0, 1, 0, 1],
    'щ': [1, 1, 0, 0, 1, 1],
    'ь': [1, 1, 1, 1, 1, 1],
    'ю': [1, 0, 1, 1, 0, 1],
    'я': [1, 1, 1, 0, 0, 1],
    '0': [0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0], 
    '1': [0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0],
    '2': [0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 0, 0],
    '3': [0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0],
    '4': [0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0],
    '5': [0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0],
    '6': [0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0], 
    '7': [0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0],
    '8': [0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 0],
    '9': [0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0],
    '-': [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1], 
    '+': [1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0],
    '*': [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0],
    '/': [1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1], 
    '=': [1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1],
    '<': [1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1],
    '>': [1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0],
    '(': [1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1],
    ')': [1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0]
}

let currentSymbol = '';
let timeoutId = null; // Для скидання таймера

function setupBrailleGrid() {
    const gridContainer = document.getElementById("braille-grid");
    gridContainer.innerHTML = '';
    
    let isExtended = braille[currentSymbol].length === 12;
    
    if (isExtended) {
        gridContainer.className = "braille-grid extended";
        
        const order = [
            0, 1, 6, 7,    
            2, 3, 8, 9,    
            4, 5, 10, 11   
        ];
        
        for (let i = 0; i < 12; i++) {
            let checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.dataset.index = order[i]; 
            gridContainer.appendChild(checkbox);
        }
    } else {
        gridContainer.className = "braille-grid";
        
        for (let i = 0; i < 9; i++) {
            let checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            
            if (i % 3 === 2) {
                checkbox.style.visibility = "hidden";
            }
            
            if (i % 3 !== 2) {
                const visibleIndex = Math.floor(i / 3) * 2 + (i % 3);
                checkbox.dataset.index = visibleIndex;
            }
            
            gridContainer.appendChild(checkbox);
        }
    }
}

function getRandomSymbol() {
    const symbols = Object.keys(braille);
    currentSymbol = symbols[Math.floor(Math.random() * symbols.length)];
    document.getElementById("random-symbol").innerText = currentSymbol;
    
    setupBrailleGrid();
}

function checkBraille() {
    const isExtended = braille[currentSymbol].length === 12;
    let selected = new Array(isExtended ? 12 : 6).fill(0);
    
    document.querySelectorAll(".braille-grid input").forEach(cb => {
        if (cb.style.visibility !== "hidden" && cb.dataset.index !== undefined) {
            const index = parseInt(cb.dataset.index);
            selected[index] = cb.checked ? 1 : 0;
        }
    });

    const resultElement = document.getElementById("result");
    if (JSON.stringify(selected) === JSON.stringify(braille[currentSymbol])) {
        resultElement.innerText = "✅ Правильно!";
    } else {
        resultElement.innerText = "❌ Неправильно!";
    }

    if (timeoutId) {
        clearTimeout(timeoutId);
    }

    timeoutId = setTimeout(() => {
        resultElement.innerText = '';
    }, 3000);
}

function nextSymbol() {
    const resultElement = document.getElementById("result");
    resultElement.innerText = ''; // Прибираємо результат
    getRandomSymbol(); // Вибираємо новий символ
}

document.addEventListener("DOMContentLoaded", () => {
    getRandomSymbol();
    document.getElementById("check-btn").addEventListener("click", checkBraille);
    document.getElementById("next-btn").addEventListener("click", nextSymbol); // Додаємо обробник для кнопки "Спробувати наступний символ"
});
