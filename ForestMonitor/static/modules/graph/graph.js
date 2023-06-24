function getData(){
    fetch('/sensor_data')
   .then(response => response.json())
   .then(data => {
       const container = document.getElementById('right-graph');
       

       data.forEach(item => {
           
           const div = document.createElement('div');
           div.classList.add('map-dot');
           div.style.left = `${item.location[0]}%`;
           div.style.top = `${item.location[1]}%`;
           if (item.timestamp != "offline")
               div.style.background = item.status > 5 ? "green" : "red";
           

           div.addEventListener('click', (event) => {
               showPopup(item, event.target);
           });

           container.appendChild(div);
       });
   });
}


function startStream(sensor_id)
{
   fetch(`/choose_stream?id=${sensor_id}`).then(response => 
    console.log(response))
}

const showPopup = (item, targetElement) => {
   const popup = document.createElement('div');
   const timestamp = item.timestamp;

   popup.classList.add('popup');
   popup.innerHTML = `
       <b>Name:</b> ${item.sensor_id}
       <br />
       <b>Location:</b> ${item.location}
       <br />
       <b>Time:</b> ${timestamp}
       <br />
       <b>Status:</b> ${item.timestamp}
       <br />
       
   `;
   
   if (item.timestamp != "offline"){
       const streamButton = document.createElement('button')
       streamButton.classList.add('button');			
       streamButton.innerText = "Start Stream"
       popup.appendChild(streamButton)
       

        streamButton.addEventListener('click', () =>
        {
            streamButton.classList.add('clicked');
            startStream(item.sensor_id);
        });
        
        streamButton.addEventListener('mouseup', function() {
            streamButton.classList.remove('clicked');
        });
   }

   document.body.appendChild(popup);

   const element = targetElement.getBoundingClientRect();
   popup.style.top = `${element.top}px`;
   popup.style.left = `${element.right}px`;
   if (item.timestamp != "offline")
       popup.style.backgroundColor = item.status < 5 ? "darkred":"darkgreen";

   const removePopup = () => {
       popup.remove();
   };

   setTimeout(() => {
       document.addEventListener('click', removePopup, { once: true });
   }, 0);

   popup.addEventListener('click', (event) => {
       event.stopPropagation();
   });
}

setInterval(getData, 2000);