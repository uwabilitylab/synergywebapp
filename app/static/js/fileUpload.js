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
  var selectList = document.createElement("select");
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

function _(el) {
  return document.getElementById(el);
}

function uploadFile(event) {
  event.preventDefault();
  event.stopPropagation();
  if(!document.getElementById('agree').checked) {
    alert('Please certify that the uploaded file contains no patient identifiers');
    return false;
  }

  var file = _("fileuploadel").files[0];
  // alert(file.name+" | "+file.size+" | "+file.type);
  var formdata = new FormData(event.currentTarget);
  var ajax = new XMLHttpRequest();
  ajax.upload.addEventListener("progress", progressHandler, false);
  ajax.addEventListener("load", completeHandler, false);
  ajax.addEventListener("error", errorHandler, false);
  ajax.addEventListener("abort", abortHandler, false);
  ajax.open("POST", "/doimport"); // http://www.developphp.com/video/JavaScript/File-Upload-Progress-Bar-Meter-Tutorial-Ajax-PHP
  //use file_upload_parser.php from above url
  ajax.send(formdata);
  document.getElementById('progressBar').hidden = false;
}

function progressHandler(event) {
  var percent = (event.loaded / event.total) * 100;
  _("progressBar").value = Math.round(percent);
  _("status").innerHTML = Math.round(percent) + "% uploaded... please wait";
}

function completeHandler(event) {
  var parameterSelection = JSON.parse(event.target.responseText);
  if (parameterSelection.status == 1) {
    document.location.href ='/parameterSelection/?fid=' + encodeURIComponent(parameterSelection.fid) + '&muscles=' + encodeURIComponent(JSON.stringify(parameterSelection.muscles)) + '&mnames=' + encodeURIComponent(JSON.stringify(parameterSelection.mnames));
  } else {
    alert(parameterSelection.message)
  }
}

function errorHandler(event) {
  console.log(event.target);
  if (event.target.status == 413) {
    alert("File uploaded is too large")
  } else {
    _("status").innerHTML = "Upload Failed";
  }
}

function abortHandler(event) {
  _("status").innerHTML = "Upload Aborted";
}
