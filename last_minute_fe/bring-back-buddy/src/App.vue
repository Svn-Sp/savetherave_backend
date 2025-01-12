<template>
  <div id="app">
    <button v-if="!isLoggedIn" @click="showLogin = true">
      Login
    </button>
    <button v-if="isLoggedIn" @click="isLoggedIn = false">
      Logout
    </button>
    <LoginComponent v-if="showLogin && !isLoggedIn" @login="onLogin" />
    <BringBackBuddyComponent v-if="isLoggedIn" />
  </div>
</template>

<script>
import LoginComponent from './components/LoginComponent.vue';
import BringBackBuddyComponent from './components/BringBackBuddyComponent.vue';

export default {
  data() {
    return {
      isLoggedIn: Boolean(localStorage.getItem('token')),
      showLogin: false,
    };
  },
  components: {
    LoginComponent,
    BringBackBuddyComponent,
  },
  methods: {
    onLogin() {
      this.isLoggedIn = true;
      this.showLogin = false;
    },
  },
};
</script>