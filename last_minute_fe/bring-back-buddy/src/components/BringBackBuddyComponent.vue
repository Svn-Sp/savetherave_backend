<!-- BringBackBuddyComponent.vue -->
<template>
  <div class="container">
    <h2>Request Bring Back Buddy</h2>
    <form @submit.prevent="requestBuddy" class="form">
      <div class="form-group">
        <input v-model="note" placeholder="Note" required class="form-control" />
      </div>
      <button type="submit" class="btn btn-primary">Request</button>
    </form>
    <p v-if="message" class="message">{{ message }}</p>
    <p v-if="error" class="error">{{ error }}</p>
    <div class="requests">
      <div v-for="request in requests" :key="request.id" class="request">
        <div class="note">{{ request.note }} </div>
        <div class="status">{{ request.status }}<span v-if="request.buddy.username">
          (Buddy: {{ request.buddy.first_name }} {{ request.buddy.last_name }})
        </span></div>
        <button v-if="!request.requester" @click="applyAsBringBackBuddy(request.id)" class="btn btn-secondary">Offer to become the Buddy</button>
        <button v-if="request.requester&&request.buddy.username" @click="reviewBuddyApplication(request.id, true)" class="btn btn-primary">Accept</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 8px;
  background-color: #f9f9f9;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

h2 {
  text-align: center;
  color: #333;
  margin-bottom: 20px;
}

.form {
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.btn {
  display: inline-block;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-primary {
  background-color: #007bff;
  color: #fff;
}

.btn-primary:hover {
  background-color: #0056b3;
}

.btn-secondary {
  background-color: #6c757d;
  color: #fff;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

.message {
  color: green;
  text-align: center;
  margin-top: 10px;
}

.error {
  color: red;
  text-align: center;
  margin-top: 10px;
}

.requests {
  margin-top: 20px;
}

.request {
  padding: 10px;
  border-bottom: 1px solid #ccc;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.note {
  font-weight: bold;
}

.status {
  color: #555;
}
</style>
<script>
import axios from 'axios';

export default {
  data() {
    return {
      partyId: '',
      note: '',
      message: '',
      error: '',
      requests: []
    };
  },
  methods: {
    async requestBuddy() {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.post(
          'http://169.231.139.207:8000/app/bringbackbuddy/request/',
          { party_id: await this.getLatestCheckInPartyId(), note: this.note },
          {
            headers: {
              Authorization: `Token ${token}`
            }
          }
        );
        this.message = response.data.message;
      } catch (error) {
        this.error = error.response.data.error;
      }
    },
    async applyAsBringBackBuddy(requestId) {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.post(
          'http://169.231.139.207:8000/app/bringbackbuddy/apply/',
          { request_id: requestId },
          { headers: { Authorization: `Token ${token}` } }
        );
        this.message = response.data.message;
      } catch (error) {
        this.error = error.response.data.message;
      }
      this.fetchInitialData();
    },
    async reviewBuddyApplication(requestId, accepted) {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.post(
          'http://169.231.139.207:8000/app/bringbackbuddy/review/',
          { request_id: requestId, accepted: accepted },
          { headers: { Authorization: `Token ${token}` } }
        );
        this.message = response.data.message;
      } catch (error) {
        this.error = error.response.data.error;
      }
      this.fetchInitialData();
    },
    async fetchInitialData() {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.post(
          'http://169.231.139.207:8000/app/bringbackbuddy/',
          { party_id: await this.getLatestCheckInPartyId() },
          {
            headers: {
              Authorization: `Token ${token}`
            }
          }
        );
        console.log(response.data);
        this.requests = response.data;
      } catch (error) {
        this.error = error.response.data.error;
      }
    },
    async getLatestCheckInPartyId() {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get('http://169.231.139.207:8000/app/user/last_check_in/', {
          headers: {
            'Authorization': `Token ${token}`
          }
        });
        return response.data.id;
      } catch (error) {
        console.error('Error fetching latest check-in:', error);
        throw error;
      }
    }
  },
  created() {
    this.fetchInitialData();
  }
};
</script>
