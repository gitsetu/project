#target illustrator

// ExpandScript, JavaScript ES3 (ECTOScript version 3) -- var used instead of let, const..

// Function to create text frame objects in Adobe Illustrator.
function createTextFrame(content, x, y) {
    var textFrame = app.activeDocument.textFrames.add();
    textFrame.contents = content; // Text content.
    textFrame.top = y;
    textFrame.left = x;
    return textFrame;
}

// Function to parse CSV data while handling quotes.
function parseCSV(data) {
    var rows = data.split('\n'); // Split the input data into rows based on newline characters.
    var result = []; // Initialize an empty array.
    
    for (var i = 0; i < rows.length; i++) {
        var cols = []; // Array for current row's column values.
        var cell = ''; // Current cell string.
        var inQuotes = false; // Flag, on when in quoted text.
        
        for (var j = 0; j < rows[i].length; j++) {
            var character = rows[i][j]; // Get current character.
            if (character === '\"') { // Comma inside quotes.
                inQuotes = !inQuotes; // If encountering a double quote, toggle flag.
            } else if (character === ',' && !inQuotes) { // Comma outside quotes.
                cols.push(cell); // If comma, push cell to columns.
                cell = ''; // Reset the cell.
            } else {
                cell += character; // Add the character to current cell.
            }
        }
        cols.push(cell); // Push the last cell for that row.
        result.push(cols); // Add the array of columns to result.
    }
    
    return result;
}

// Function to import CSV data from a file.
function importCSV() {
    // fileRef references a file object.
    var fileRef = new File ("~/Desktop/test.csv"); // this is the hardcoded option
    // var fileRef = File.openDialog("Select a CSV file", "*.csv"); // this lets user select a file
    
    if (fileRef) { // If file exists/selected.
        fileRef.open('r'); // Open the file in read mode.
        var data = fileRef.read(); // Reads the entire content of the file and stores it in the variable data as a string.
        fileRef.close(); // Once readed, tell system to close the file.
        return data;
    } else { // Notification error if file not selected, or does not exist.
        alert("No file selected!");
        return null;
    }
}

// Import CSV data.
var data = importCSV();
if (data) {
    // Split the data and parse it.
    var parsedData = parseCSV(data);
    
    // Initialise position for text frames, top-left.
    var xOffset = 0;
    var yOffset = 0;

    // Make sure there's an open document.
    if (app.documents.length > 0) {
        for (var i = 1; i < parsedData.length; i++) {
            var values = parsedData[i];

            for (var j = 0; j < values.length; j++) {
                // Create a text frame for each value.
                var content = parsedData[0][j] + ": " + values[j];  // Label with value.
                createTextFrame(content, xOffset, yOffset);
                yOffset -= 20;  // Move down for the next line.
            }
            
            // Reset yOffset for the next product's data.
            yOffset -= 40;  // Add space between different products.
        }
    } else {
        alert("Please open a document first!");
    }

    // Finalize the document to preserve changes.
    app.activeDocument.selection = null; // Clear the current selection.
}
