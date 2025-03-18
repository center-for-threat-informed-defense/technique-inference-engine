<template>
  <div class="navigation-footer-control">
    <div class="navigation-footer-main theme-dark">
      <div class="navigation-footer-contents">
        <div class="ctid-section">
          <div class="ctid-info">
            <h3>The Center for Threat-Informed Defense</h3>
            <p class="site-description">
              The <a href="https://ctid.mitre.org/" target="_blank">Center for
                Threat-Informed Defense</a> is a non-profit, privately funded research and
              development
              organization. Our mission is to advance the state of the art and the state of the practice in
              threat-informed defense globally.
            </p>
            <div class="footer-row">
              <img class="ctid-logo" src="@/assets/images/engenuity_ctid_logo.png"
                alt="Center for Threat-Informed Defense">
              <div class="social-icons">
                <a href="mailto:ctid@mitre.org?subject=Technique%20Inference%20Engine">
                  <IconEmail aria-label="email the center for threat-informed defense" />
                </a>
                <a href="https://www.linkedin.com/showcase/center-for-threat-informed-defense/">
                  <IconLinkedIn aria-label="center for threat-informed defense linkedin" />
                </a>
                <a href="https://www.youtube.com/playlist?list=PLALq3Th79NnpUkRy8TUYVBKvysCp9xwNh">
                  <IconYoutube aria-label="center for threat-informed defense youtube" />
                </a>
                <a href="https://github.com/center-for-threat-informed-defense/technique-inference-engine">
                  <IconGitHub aria-label="center for threat-informed defense github" />
                </a>
              </div>
            </div>
          </div>
          <div class="ctid-links">
            <div class="link-list">
              <h5>About Us</h5>
              <ul>
                <li>
                  <a href="https://ctid.mitre.org/">
                    Home
                  </a>
                </li>
                <li>
                  <a href="https://ctid.mitre.org/projects/">
                    Our Work
                  </a>
                </li>
                <li>
                  <a href="https://ctid.mitre.org/membership/">
                    Membership
                  </a>
                </li>
                <li>
                  <a href="https://ctid.mitre.org/get-involved/">
                    Get Involved
                  </a>
                </li>
              </ul>
            </div>
            <div class="link-list">
              <h5>Related Projects</h5>
              <ul>
                <li>
                  <a href="https://center-for-threat-informed-defense.github.io/attack-flow/">
                    Attack Flow
                  </a>
                </li>
                <li>
                  <a href="https://center-for-threat-informed-defense.github.io/mappings-explorer/">
                    Mappings Explorer
                  </a>
                </li>
                <li>
                  <a href="https://center-for-threat-informed-defense.github.io/summiting-the-pyramid/">
                    Summiting the Pyramid
                  </a>
                </li>
                <li>
                  <a href="https://github.com/center-for-threat-informed-defense/tram/wiki">
                    TRAM
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div class="disclosures-section">
          <small>
            Copyright © 2024 MITRE. Approved for public release. Document number(s) CT0124.
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
import IconEmail from "../Icons/IconEmail.vue"
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
  margin: scale.size("s") 0px scale.size("xl");
}

.footer-row {
  display: flex;
  gap: scale.size("xl");
}

.social-icons {
  @include scale.grid-layout-dynamic(4, "s", 1, "s");
}

.social-icons a {
  height: scale.size("xl");
  width: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 100%;
}

.social-icons a svg {
  height: 100%;
  width: 100%;
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
