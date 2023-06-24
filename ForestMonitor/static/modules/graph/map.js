function render_map(){
    const apiKey = 'AmTH_UlyKQ6yxkEJwDqYJgVXS9yxSBBiIto9lFnKUjk9TNIf2FUFiazerKfb7Y6_';
    const latitude = 44.76515999;
    const longitude = 20.4402974;
    const zoom = 15;
    const imageSize = '700,700';
    // https://dev.virtualearth.net/REST/v1/Imagery/Map/Aerial/44.76516,20.4402974/15?mapSize=700,700&key=AmTH_UlyKQ6yxkEJwDqYJgVXS9yxSBBiIto9lFnKUjk9TNIf2FUFiazerKfb7Y6_
    const satImgUrl = `https://dev.virtualearth.net/REST/v1/Imagery/Map/Aerial/${latitude},${longitude}/${zoom}?mapSize=${imageSize}&key=${apiKey}`;
    
    const container = document.getElementById('right-graph');
    const imgElement = document.createElement('img');
    imgElement.src = satImgUrl;
    container.appendChild(imgElement);
}
render_map()
