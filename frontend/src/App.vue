<template>
  <div id="app">
    <div class="phone-wrapper">
      <div class="phone-frame">
        <div class="notch">
          <div class="camera"></div>
          <div class="speaker"></div>
        </div>
        
    
        <div class="screen">
          <router-view/> 
        </div>
      </div>
      
      <div class="home-indicator"></div>
      
     
      <div class="side-buttons">
        <div class="volume-up"></div>
        <div class="volume-down"></div>
        <div class="power-button"></div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App',
}
</script>

<style>
html, body {
    margin: 0;
    padding: 0;
    height: 100%; 
    background-color: #e0e0e0; 
    overflow-x: hidden; 
}

#app {
    font-family: Avenir, Helvetica, Arial, sans-serif;
    color: #2c3e50;
    display: flex;
    justify-content: center; 
    align-items: center;
    height: 100vh; 
    width: 100%;
    margin: 0;
    padding: 40px; 
    box-sizing: border-box;
}

.phone-wrapper {
    position: relative;
    width: 100%; 
    max-width: 420px;
    height: 100%;
    max-height: 900px;
}


.phone-frame {
    width: 100%;
    height: 100%;
    background: #1a1a1a;
    border-radius: 55px;
    padding: 8px; 
    box-shadow: 
        0 0 0 3px #0a0a0a,
        0 0 0 14px #2a2a2a,
        0 25px 70px rgba(0, 0, 0, 0.6);
    position: relative;
    box-sizing: border-box;
}


.notch {
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 160px;
    height: 28px; 
    background: #1a1a1a;
    border-radius: 0 0 20px 20px;
    z-index: 100;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
}

.camera {
    width: 12px;
    height: 12px;
    background: #333;
    border-radius: 50%;
    border: 1px solid #555;
}

.speaker {
    width: 50px;
    height: 6px;
    background: #222;
    border-radius: 3px;
}


.screen {
    width: 100%;
    height: 100%;
    background: #f5f5f7;
    border-radius: 48px; 
    overflow: hidden;
    position: relative;
}


.home-indicator {
    position: absolute;
    bottom: 18px;
    left: 50%;
    transform: translateX(-50%);
    width: 150px;
    height: 5px;
    background: rgba(255, 255, 255, 0.5);
    border-radius: 3px;
    z-index: 10;
}


.side-buttons {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
}

.volume-up,
.volume-down,
.power-button {
    position: absolute;
    background: #2a2a2a;
    border-radius: 2px;
}


.volume-up {
    width: 5px;
    height: 70px;
    left: -5px;
    top: 200px;
    box-shadow: inset -1px 0 2px rgba(0, 0, 0, 0.5);
}

.volume-down {
    width: 5px;
    height: 70px;
    left: -5px;
    top: 290px;
    box-shadow: inset -1px 0 2px rgba(0, 0, 0, 0.5);
}

.power-button {
    width: 5px;
    height: 90px;
    right: -5px;
    top: 245px;
    box-shadow: inset 1px 0 2px rgba(0, 0, 0, 0.5);
}

.screen .welcome-container {
    width: 100%; 
    height: 100%;
}

/*모바일 환경 프레임 제거 css*/
@media (max-width: 500px) or (max-height: 950px) {
    #app {
        padding: 0;
    }
    
    .phone-wrapper {
        max-width: 100%;
        max-height: 100%;
    }
    
    .phone-frame {
        border-radius: 0;
        padding: 0;
        box-shadow: none;
        background: transparent;
    }
    
    .notch,
    .home-indicator,
    .side-buttons {
        display: none;
    }
    
    .screen {
        border-radius: 0;
    }
}

button:focus {
    outline: none; 
}
</style>