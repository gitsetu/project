#target illustrator

// Function to create text frames
function createTextFrame(content, x, y) {
    var textFrame = app.activeDocument.textFrames.add();
    textFrame.contents = content;
    textFrame.top = y;
    textFrame.left = x;
    return textFrame;
}

// Function to parse CSV data while handling quotes
function parseCSV(data) {
    var rows = data.split('\n');
    var result = [];
    
    for (var i = 0; i < rows.length; i++) {
        var cols = [];
        var cell = '';
        var inQuotes = false;
        
        for (var j = 0; j < rows[i].length; j++) {
            var character = rows[i][j];
            if (character === '\"') {
                inQuotes = !inQuotes; // Toggle the quotes flag
            } else if (character === ',' && !inQuotes) {
                cols.push(cell);
                cell = ''; // Reset the cell
            } else {
                cell += character; 
            }
        }
        cols.push(cell); // Push the last cell
        result.push(cols);
    }
    
    return result;
}

// Function to import CSV data from a file
function importCSV() {
    var fileRef = File.openDialog("Select a CSV file", "*.csv");
    if (fileRef) {
        fileRef.open('r');
        var data = fileRef.read();
        fileRef.close();
        return data;
    } else {
        alert("No file selected!");
        return null;
    }
}

// Import CSV data
var data = importCSV();
if (data) {
    // Split the data and parse it
    var parsedData = parseCSV(data);
    
    // Set position variables for text frames
    var xOffset = 0;
    var yOffset = 0;

    // Make sure there's an open document
    if (app.documents.length > 0) {
        for (var i = 1; i < parsedData.length; i++) {
            var values = parsedData[i];

            for (var j = 0; j < values.length; j++) {
                // Create a text frame for each value
                var content = parsedData[0][j] + ": " + values[j];  // Label with value
                createTextFrame(content, xOffset, yOffset);
                yOffset -= 20;  // Move down for the next line
            }
            
            // Reset yOffset for the next product's data
            yOffset -= 40;  // Add space between different products
        }
    } else {
        alert("Please open a document first!");
    }

    // Finalize the document to preserve changes
    app.activeDocument.selection = null;
}
