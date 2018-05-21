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
  this.filterColumns = [];
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
  var array = ["", "Other"];
  var text  =["Don't Include", "Other"];
  var lowarray = ["Add_Mag", "Gas_Med", "Glu_Max", "Glu_Med", "Lat_Ham", "Med_Ham", "Pre_Bre", "Rec_Fem", "Soleus", "Ten_Fas_Lat", "Tib_Ant", "Vas_Med", "Vas_Lat"];
  var lowtext = ["Adductor Magnus",  "Gastrocnemius Medialis", "Gluteus Maximus", "Gluteus Medius", "Lateral Hamstring", "Medial Hamstring", "Peroneus Brevis", "Rectus Femoris", "Soleus", "Tensor Fasciae Latae", "Tibialis Anterior", "Vastus Medialis", "Vastus Lateralis"];
  var trunkarray = ["Ere_Spi", "Ext_Obl", "Lat_Dor", "Rec_Abd", "Spleni", "Trap_Inf", "Tra_Sup"];
  var trunktext = ["Erector Spinae", "External Obliques", "Latissimus Dorsi", "Rectus Abdmoninus", "Splenius", "Trapizius Inferior", "Trapizius Superior"];
  var higharray =["Ant_Del", "Bic_Bra", "Pos_Del", "Tri_Bra"];
  var hightext= ["Anterior Deltoid", "Biceps Brachii", "Posterior Deltoid", "Triceps Brachii"];
  var selectList = document.createElement('select');
  var option = document.createElement("option");
  option.value = array[0];
  option.text = text[0];
  selectList.appendChild(option);
  var lowoptgroup = document.createElement('optgroup');
  lowoptgroup.label = 'Lower Limb Muscles';
  // selectList.appendChild(lowoptgroup);
  for (var j = 0; j < lowarray.length; j++) {
      var option = document.createElement("option");
      option.value = lowarray[j];
      option.text = lowtext[j];
      lowoptgroup.appendChild(option);
  }
  selectList.appendChild(lowoptgroup);
  var trunkoptgroup = document.createElement('optgroup');
  trunkoptgroup.label = 'Trunk Muscles';
  // selectList.appendChild(lowoptgroup);
  for (var j = 0; j < trunkarray.length; j++) {
      var option = document.createElement("option");
      option.value = trunkarray[j];
      option.text = trunktext[j];
      trunkoptgroup.appendChild(option);
  }
  selectList.appendChild(trunkoptgroup);
  var highoptgroup = document.createElement('optgroup');
  highoptgroup.label = 'Upper Limb Muscles';
  // selectList.appendChild(lowoptgroup);
  for (var j = 0; j < higharray.length; j++) {
      var option = document.createElement("option");
      option.value = higharray[j];
      option.text = hightext[j];
      highoptgroup.appendChild(option);
  }
  selectList.appendChild(highoptgroup);
  var option = document.createElement("option");
  option.value = array[1];
  option.text = text[1];
  selectList.appendChild(option);
  //create the column definitions
  var fileTableHeading = _createElement('thead');
  var headerCols = this.previewData[headerLineIndex], headerEl = _createElement('tr'), headerColEl, self = this;

  //for(var i=0;i<headerCols.length;i++) {
  for(var i=0;i<this.filterColumns.length;i++) {
    headerColEl = _createElement('th', null, headerCols[i]);
    headerEl.appendChild(headerColEl);
    var columnSelect = selectList.cloneNode(true);
    columnSelect.setAttribute('name', 'muscle[' + this.filterColumns[i].index + ']');
    headerColEl.appendChild(columnSelect);
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
            self.filterColumns.push({
              index: j,
              emgIndex: k,
              muscle: null
            });
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
