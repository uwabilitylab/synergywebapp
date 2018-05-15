"use strict";

/**
 * Convenience wrapper for document.createElement()
 * @param string tagName
 * @param Object attributes
 * @param mixed childNodes
 * @return HTMLElement
 */
function _createElement(tagName, attributes, childNodes) {
  var el = document.createElement(tagName), childType = typeof childNodes;
  for(var name in attributes) {
    el.setAttribute(name, attributes[name]);
  }

  if(childNodes instanceof HTMLElement) {
    el.appendChild(childNodes);
  } else if(childType == 'string' || childType == 'number') {
    el.appendChild(document.createTextNode(childNodes));
  } else if(childType == 'object') { //i.e. a list of pre-created DOM elements
    if(childNodes instanceof Array) {
      for(var i=0;i<childNodes.length;i++) {
        el.appendChild(childNodes[i])
      }
    } else {
      while(childNodes.firstChild) {
        el.appendChild(childNodes.firstChild);
      }
    }
  }
  return el;
}
function _getElement(tagName, attributes) {
  var el = document.createElement(tagName);
  // for(var name in attributes) {
  //   el.setAttribute(name, attributes[name]);
  // }
  el.appendChild(document.getElementById(attributes));

  // if(childNodes instanceof HTMLElement) {
  //   el.appendChild(childNodes);
  // } else if(childType == 'string' || childType == 'number') {
  //   el.appendChild(document.createTextNode(childNodes));
  // } else if(childType == 'object') { //i.e. a list of pre-created DOM elements
  //   if(childNodes instanceof Array) {
  //     for(var i=0;i<childNodes.length;i++) {
  //       el.appendChild(childNodes[i])
  //     }
  //   } else {
  //     while(childNodes.firstChild) {
  //       el.appendChild(childNodes.firstChild);
  //     }
  //   }
  // }
  return el;
}
/**
 * Class for managing a file's preview interface
 * @param HTMLElement container
 * @param Object fileData
 */
function FilePreview(fileInput, previewContainer) {
  this.fileInput = fileInput;
  this.previewContainer = previewContainer;

  this.resetState();
}
FilePreview.prototype.resetState = function() {
  this.previewData = [];
};

/**
 * Renders the file's parsed data into a table
 * @param int headerLineIndex
 * @param int previewLineCount
 */
FilePreview.prototype.createPreview = function(headerLineIndex, previewLineCount) {
  //clear the file preview, in case previously populated
  while(this.previewContainer.childNodes.length > 0) {
    this.previewContainer.removeChild(this.previewContainer.firstChild);
  }
  var previewTableEl = _createElement('table', {'class': 'file_preview', 'id': 'table_file_preview'});

  //create the column definitions
  var fileTableHeading = _createElement('thead');
  var headerCols = this.previewData[headerLineIndex], headerEl = _createElement('tr'), headerColEl, self = this;
  for(var i=0;i<headerCols.length;i++) {
    headerColEl = _createElement('th', null, headerCols[i]);
    headerEl.appendChild(headerColEl);
  }
  this.headerEl = headerEl;

  fileTableHeading.appendChild(headerEl);

  var fileTableBody = _createElement('tbody'), dataRowEl, dataColEl, dataCols, previewRows = Math.min(previewLineCount, this.previewData.length);
  for(var i=headerLineIndex+1;i<previewRows;i++) {
    dataRowEl = _createElement('tr');
    dataCols = this.previewData[i];

    for(var c=0;c<dataCols.length;c++) {
      dataColEl = _createElement('td', null, dataCols[c]);
      dataRowEl.appendChild(dataColEl);
    }
    fileTableBody.appendChild(dataRowEl);
  }
  var includeRowEl = _createElement('tr');
  var includeColEl;
  for(var i=0;i<dataCols.length;i++) {
    includeColEl = document.createElement('td');
    var tableLabel = _createElement('label', {'class': 'radio'});
    var but = _createElement('input', {'type': 'checkbox', 'id':String(i), 'name':'includeAll', 'value':String(i)});
    var lab = _createElement('label', {'for':'include'});
    lab.innerHTML = 'Include';
    // but.id = i;
    // but.type = "radio";
    // but.name = "include";
    // but.value = "Muscle" + i+1;
    // but.label = "Include";
    // but.innerHTML = 'Include';
    // tableLabel.appendChild(but);
    // tableLabel.appendChild(lab);
    includeColEl.appendChild(but);
    includeColEl.appendChild(lab);
    includeRowEl.appendChild(includeColEl);
  }
  fileTableBody.appendChild(includeRowEl);
  var muscleRowEl = _createElement('tr');
  var muscleColEl;
  var array = ["", "Ext_Obl", "Rec_Abd", "Add_Mag", "Ten_Fas_Lat", "Glu_Med", "Glu_Max", "Vas_Lat", "Rec_Fem", "Med_Ham", "Lat_Ham", "Gas_Med", "Soleus", "Tib_Ant", "Pre_Bre", "Ere_Spi"];
  var text = ["Select a muscle", "External Obliques", "Rectus Abdmoninus", "Adductor Magnus", "Tensor Fasciae Latae", "Gluteus Medius", "Glueteus Maximus", "Vastus Lateralis", "Rectus Femoris", "Medial Hamstring", "Lateral Hamstring", "Gastrocnemius Medialis", "Soleus", "Tibialis Anterior", "Peroneus Brevis", "Erector Spinae"];
  for(var i=0;i<dataCols.length;i++) {
    muscleColEl = document.createElement('td');
    var selectList = document.createElement('select');
    selectList.id = "mySelect";

    for (var j = 0; j < array.length; j++) {
        var option = document.createElement("option");
        option.value = array[j];
        option.text = text[j];
        selectList.appendChild(option);
    }
    muscleColEl.appendChild(selectList);
    muscleRowEl.appendChild(muscleColEl);
  }
  fileTableBody.appendChild(muscleRowEl);

  previewTableEl.appendChild(fileTableHeading);
  previewTableEl.appendChild(fileTableBody);
  this.previewContainer.appendChild(previewTableEl);
};

/**
 * Parses the file the user has selected
 * @param int previewLineCount
 */
FilePreview.prototype.readFile = function(headerLineIndex, previewLineCount) {
  this.resetState(); //clear any previously-loaded data

  var reader = new FileReader(), self = this, rowDelimiter = /\r\n?|\n/, colDelimiter = ',', sliceSize = 65536; //sliceSize should be big enough to read in at least 1 row from the file
    reader.onload = function (readEvent) {
    //parse the file's data.  TODO: add error checks
    var i, j, k, fileLines = readEvent.target.result.split(rowDelimiter), headerLine, rawLine, filteredLine;
    fileLines.pop(); //remove last line since it's probably incomplete

    var EMGcols = [];
    for(i=0;i<fileLines.length;i++) {
			rawLine = fileLines[i].split(colDelimiter);
			//CLAIRE: here's where you can do the column filtering
			if(i == headerLineIndex) { //determine which columns are the EMG columns
				filteredLine = rawLine; //placeholder
        k=0;
        fileLines[i] = [];
        for(j=0;j<filteredLine.length;j++) {
          if(filteredLine[j].indexOf("EMG") !== -1) {
            EMGcols[k] = j;
            console.log(filteredLine[j]);
            fileLines[i][k] = filteredLine[j];
            k++;
          }
        }
			} else if(i > headerLineIndex) { //i.e. the file's data points
        fileLines[i] = [];
				filteredLine = rawLine; //placeholder
        k=0;
        for(j=0;j<filteredLine.length;j++) {
          if(EMGcols.includes(j)) {
            fileLines[i][k] = filteredLine[j];
            k++;
          }
        }
			}

			// fileLines[i] = filteredLine;
		}
    self.previewData = fileLines;

    //and create the preview table
      self.createPreview(headerLineIndex, previewLineCount);
    };

    //we only need the first part of the file for the preview
    var fileSection = this.fileInput.files[0].slice(0, sliceSize);
    reader.readAsText(fileSection);
};
