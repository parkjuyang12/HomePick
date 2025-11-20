<template>
  <div id="app">
    <router-view/> 
  </div>
</template>

<script>
// 기존의 HelloWorld나 ApiTest 임포트 내용을 모두 지웁니다.
export default {
  name: 'App',
  // components: {} 항목도 삭제하거나 비워둡니다.
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>