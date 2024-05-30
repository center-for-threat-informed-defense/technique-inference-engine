<template>
  <div class="navigation-footer-control">
    <div class="navigation-buffer"></div>
    <div class="navigation-footer-main theme-dark">
      <div class="navigation-footer-contents">
        <div class="site-info">
          <div class="site-logo">
            <div class="logo-container"></div>
            <RouterLink class="navigation-link logo" to="/">
              Technique Inference Engine
            </RouterLink>
          </div>
          <p class="site-description">
            Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
            tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
            quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
            consequat.
          </p>
          <div class="social-links">
            <img src="@/assets/images/engenuity_ctid_logo.png">
            <div class="social-icons">
              <a class="box-link" href="/about">
                <IconEmail />
              </a>
              <a class="box-link" href="/about">
                <IconLinkedIn />
              </a>
              <a class="box-link" href="/about">
                <IconYoutube />
              </a>
              <a class="box-link" href="/about">
                <IconGitHub />
              </a>
            </div>
          </div>
        </div>
        <div class="site-links">
          <div class="link-list">
            <h4>Online</h4>
            <ul>
              <li><a href="/">E-mail</a></li>
              <li><a href="/about">LinkedIn</a></li>
              <li><a href="/about">YouTube</a></li>
              <li><a href="/about">GitHub</a></li>
            </ul>
          </div>
          <div class="link-list">
            <h4>Overview</h4>
            <ul>
              <li>
                <RouterLink class="body" to="/">Home</RouterLink>
              </li>
              <li>
                <RouterLink class="body" to="/about">About</RouterLink>
              </li>
              <li>
                <RouterLink class="body" to="/about">Methodology</RouterLink>
              </li>
              <li>
                <RouterLink class="body" to="/about">Help</RouterLink>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
// Dependencies
import { defineComponent } from "vue";
// Components
import { RouterLink } from 'vue-router'
import IconEmail from "@/components/Icons/IconEmail.vue"
import IconGitHub from "../Icons/IconGitHub.vue";
import IconYoutube from "../Icons/IconYoutube.vue";
import IconLinkedIn from "../Icons/IconLinkedIn.vue";

export default defineComponent({
  name: "NavigationHeader",
  components: { RouterLink, IconEmail, IconGitHub, IconYoutube, IconLinkedIn }
});
</script>

<style lang="scss" scoped>
@use "@/assets/styles/engenuity_scaling_system" as scale;

/** === Main Control === */

.navigation-link.logo {
  @include scale.h3;
  text-decoration: none;
}

.navigation-buffer {
  width: 100%;
  height: scale.size("xxh");
  margin-top: scale.size("xxh");
  background: url("@/assets/images/ctid_stripe_pattern.png");
}

.navigation-footer-main {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  padding: scale.size("xxh");
}

.navigation-footer-contents {
  display: flex;
  justify-content: space-between;
  width: 100%;
  height: 100%;
  max-width: scale.$max-width;
}

/** === Site Info === */

.site-info {
  width: 50%;
}

.site-logo {
  display: flex;
  align-items: center;
}

.logo-container {
  @include scale.box("h");
  border: solid 1px;
  margin-right: scale.size("m");
}

.site-description {
  margin-top: scale.size("xxl");
  margin-bottom: scale.size("h");
}

.social-links {
  display: flex;
  align-items: center;
}

.social-links img {
  height: 26px;
  margin-right: 25px;
}

.social-icons {
  @include scale.grid-layout-dynamic(4, "m", 1, "m");
}

.social-icons a {
  display: flex;
  align-items: center;
  justify-content: center;
}

.box-link {
  @include scale.box("xxl");
}

/** === Site Links === */

.site-links {
  display: flex;
  justify-content: right;
  width: 50%;
}

.link-list {
  text-align: right;
  margin-right: 70px;
}

.link-list:last-child {
  margin-right: 0px;
}

.link-list ul {
  padding: 0px;
}

.link-list li {
  list-style: none;
  margin-top: 12px;
}
</style>
