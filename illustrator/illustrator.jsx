#target illustrator

// Sample data string from CSV format
var data = "barcode_number,product_name,list_of_ingredients,net_quantity,e_mark,drained_weight,best_before_date,batch_number,storage_instructions,supplier_address,nutritional_information,energy_kj_kcal,fat_total,fat_saturates,fat_mono-saturates,carbohydrates,fibre,protein,salt,country_of_origin,alcohol_content,acidity_content,instructions_of_use,dietary_claims,marketing_spiel,brand_logo,reciclable_packaging,label_width_mm,label_height_mm,allergens,clean_label\n8720182774798,Real Mayonnaise,\"Rapeseed oil (78%), EGG & EGG yolk (7.9%), water, spirit vinegar, sugar, salt, flavourings, lemon juice concentrate, antioxidant (calcium disodium EDTA), paprika extract.\",400g,TRUE,,April 2026,L26001,Refrigerate after opening and use within 3 months. Do not freeze.,\"Unilever UK, Hellmann's, Freepost ADM 3940, London, SW1A 1YR. Unilever Ireland, 20 Riverwalk, Citywest, Dublin 24.\",TRUE,3011kJ / 720kcal,79g,6.1g,50g,1.4g,<0.5g,1.1g,1.2g,United Kingdom,,\"It is perfect as an ingredient, filling, topping, dip or accompaniment to meals including sandwiches and salads.\",Suitable for vegetarians.,Rich & Creamy Flavour,,,,,TRUE,Free from preservatives and artificial colours.";

// Function to create text frames
function createTextFrame(content, x, y) {
    var textFrame = app.activeDocument.textFrames.add();
    textFrame.contents = content;
    textFrame.top = y;
    textFrame.left = x;
    return textFrame;
}

// Split the data into lines and columns
var lines = data.split('\n');
var headers = lines[0].split(',');

// Set position variables for text frames
var xOffset = 0;
var yOffset = 0;

// Make sure there's an open document
if (app.documents.length > 0) {
    for (var i = 1; i < lines.length; i++) {
        var values = lines[i].split(',');

        for (var j = 0; j < values.length; j++) {
            // Create a text frame for each value
            var content = headers[j] + ": " + values[j];  // Label with value
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
