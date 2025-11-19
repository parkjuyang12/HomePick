<template>
  <img alt="Vue logo" src="./assets/logo.png">
  <HelloWorld msg="Welcome to Your Vue.js App"/>
  
  <ApiTest/>  </template>

<script>
import HelloWorld from './components/HelloWorld.vue'
import ApiTest from './components/ApiTest.vue' // 👈 새로 추가

export default {
  name: 'App',
  components: {
    HelloWorld,
    ApiTest // 👈 새로 추가
  }
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
