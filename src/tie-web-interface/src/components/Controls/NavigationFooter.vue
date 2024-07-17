<template>
  <div class="navigation-footer-control">
    <div class="navigation-buffer"></div>
    <div class="navigation-footer-main theme-dark">
      <div class="navigation-footer-contents">
        <div class="ctid-section">
          <div class="ctid-info">
            <img class="ctid-logo" src="@/assets/images/engenuity_ctid_logo.png">
            <p class="site-description">
              The <a href="">Center for Threat-Informed Defense</a> is a non-profit, privately funded research and
              development
              organization. Our mission is to advance the state of the art and the state of the practice in
              threat-informed defense globally.
            </p>
            <div class="social-icons">
              <a href="mailto:ctid@mitre-engenuity.org?subject=Technique%20Inference%20Engine">
                <IconEmail />
              </a>
              <a href="https://www.linkedin.com/showcase/center-for-threat-informed-defense/">
                <IconLinkedIn />
              </a>
              <a href="https://www.youtube.com/@mitreengenuity">
                <IconYoutube />
              </a>
              <a href="https://github.com/center-for-threat-informed-defense/technique-inference-engine">
                <IconGitHub />
              </a>
            </div>
          </div>
          <div class="ctid-links">
            <div class="link-list">
              <h5>About Us</h5>
              <ul>
                <li>
                  <a href="https://mitre-engenuity.org/cybersecurity/center-for-threat-informed-defense/">
                    Home
                  </a>
                </li>
                <li>
                  <a href="https://mitre-engenuity.org/cybersecurity/center-for-threat-informed-defense/our-work/">
                    Our Work
                  </a>
                </li>
                <li>
                  <a href="https://mitre-engenuity.org/cybersecurity/center-for-threat-informed-defense/participants/">
                    Membership
                  </a>
                </li>
                <li>
                  <a href="https://mitre-engenuity.org/cybersecurity/center-for-threat-informed-defense/membership/">
                    Get Involved
                  </a>
                </li>
              </ul>
            </div>
            <div class="link-list">
              <h5>Related Projects</h5>
              <ul>
                <li><a href="/">Attack Flow</a></li>
                <li><a href="/about">Mappings Explorer</a></li>
                <li><a href="/about">Summiting the Pyramid</a></li>
                <li><a href="/about">TRAM</a></li>
              </ul>
            </div>
            <div class="link-list">
              <h5>TIE</h5>
              <ul>
                <li>
                  <a href="#">
                    Home
                  </a>
                </li>
                <li>
                  <a href="#">
                    About
                  </a>
                </li>
                <li>
                  <a href="#">
                    Methodology
                  </a>
                </li>
                <li>
                  <a href="#">
                    Help
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div class="disclosures-section">
          <small>
            Copyright © 2024 MITRE Engenuity. Approved for public release. Document number(s) PUT_PRS_NUMBER_HERE.
          </small>
        </div>

      </div>
    </div>
  </div>
</template>

<script lang="ts">
// Dependencies
import { defineComponent } from "vue";
// Components
import IconEmail from "@/components/Icons/IconEmail.vue"
import IconGitHub from "../Icons/IconGitHub.vue";
import IconYoutube from "../Icons/IconYoutube.vue";
import IconLinkedIn from "../Icons/IconLinkedIn.vue";

export default defineComponent({
  name: "NavigationFooter",
  components: { IconEmail, IconGitHub, IconYoutube, IconLinkedIn }
});
</script>

<style lang="scss" scoped>
@use "@/assets/styles/engenuity_scaling_system" as scale;
@use "@/assets/styles/engenuity_color_system" as color;

/** === Main Control === */

.navigation-buffer {
  width: 100%;
  height: scale.size("xxh");
  background: url("@/assets/images/ctid_stripe_pattern.png");
  background-size: 14px 14px;
}

.navigation-footer-main {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 0;
  padding: scale.size("xxh");
}

.navigation-footer-contents {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  max-width: scale.$max-width;
}

/** === CTID Footer === */

.ctid-section {
  display: grid;
}

.ctid-info {
  display: flex;
  flex-direction: column;
  align-items: start;
}

.ctid-logo {
  max-height: 26px;
  max-width: 100%;
}

.site-description {
  margin: scale.size("xl") 0px;
}

.social-icons {
  @include scale.grid-layout-dynamic(4, "m", 1, "m");
}

.social-icons a {
  @include scale.box("xxl");
  @include color.box-link;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ctid-links {
  display: flex;
}

.link-list ul {
  padding: 0px;
  list-style: none;
}

.link-list li {
  margin-top: scale.size("m");
}

.link-list a {
  text-decoration: none;
}

/** === Disclosures Footer === */

.disclosures-section {
  padding-top: scale.size("s");
  border-top: solid 1px;
  margin-top: scale.size("xxl");
}


/** === Footer (Desktop) === */

@include scale.above-desktop-width() {

  .ctid-section {
    grid-template-columns: 1fr 1fr;
    column-gap: scale.size("xxl");
  }

  .ctid-links {
    justify-content: space-evenly;
  }

}

/** === Footer (Mobile) === */

@include scale.at-and-below-desktop-width() {

  .ctid-section {
    grid-template-rows: auto auto;
    row-gap: scale.size("xxl");
  }

  .ctid-links {
    justify-content: space-between;
  }

}

/** === Footer (Sub-Mobile) === */

@include scale.below-mobile-width() {

  .ctid-links {
    flex-direction: column;
  }

  .link-list {
    margin-bottom: scale.size("xxl");
  }

  .link-list:last-child {
    margin-bottom: 0px;
  }

}
</style>
