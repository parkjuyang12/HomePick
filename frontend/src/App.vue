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
    /* ... (기존 스타일 유지) */
    position: relative;
    width: 100%; 
    max-width: 420px;
    /* 🟢 phone-wrapper에 height: 100% 추가 (App #app으로부터 높이 상속) */
    height: 100%; 
    max-height: 900px;
}

.phone-frame {
    width: 100%;
    height: 100%;
    background: #1a1a1a;
    border-radius: 55px;
    padding: 8px; 
    /* 🟢 phone-frame에 display: flex 추가 (높이 100%를 상속받기 위함) */
    display: flex; 
    box-shadow: 
        0 0 0 3px #0a0a0a,
        0 0 0 14px #2a2a2a,
        0 25px 70px rgba(0, 0, 0, 0.6);
    position: relative;
    box-sizing: border-box;
}

.screen {
    width: 100%;
    height: 100%; 
    background: #f5f5f7;
    border-radius: 48px; 
    overflow: auto; 
    position: relative;
    -webkit-overflow-scrolling: touch; 
}

.screen::-webkit-scrollbar {
    display: none;
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

.home-indicator {
  position: absolute;         
  bottom: 20px;             /* 하단 여백 */
  left: 50%;
  transform: translateX(-50%);

  width: 180px;
  height: 5px;
  background: rgba(5, 5, 5, 0.5);
  border-radius: 3px;

  z-index: 999;             /* 앱 UI 위에 */
  pointer-events: none;     /* 클릭 방해 안 함 */
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
        /* 🟢 추가: phone-wrapper도 모바일 환경에서 100% 높이를 갖도록 */
        height: 100vh; 
    }
    
    .phone-frame {
        border-radius: 0;
        padding: 0;
        box-shadow: none;
        background: transparent;
        /* 🟢 추가: phone-frame도 100% 높이를 갖도록 */
        height: 100%;
    }
    
    .notch,
    .home-indicator,
    .side-buttons {
        display: none;
    }
    
    .screen {
        border-radius: 0;
        /* 🟢 수정/추가: screen이 100% 높이를 갖도록 */
        height: 100%; 
    }
}

button:focus {
    outline: none; 
}
</style>