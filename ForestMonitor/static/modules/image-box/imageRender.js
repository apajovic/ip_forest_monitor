function getImage(){
    const leftGraph = document.getElementById('left-graph');
    fetch('/render_stream')
          .then(response => response.text())
          .then(imageData => {
              while (leftGraph.firstChild) {
                  leftGraph.firstChild.remove();
              }

              const imageElement = document.createElement('img');
              imageElement.src = imageData;
              leftGraph.appendChild(imageElement);
          })
          .catch(error => {
              console.error('Error:', error);
          });
};

const interval = setInterval(getImage, 2000);
