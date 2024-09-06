<template>
  <div class="about">
    <div class="about-contents">
      <h1 id="overview">Overview</h1>
      <p>
        Describing adversarial behaviors in the form of tactics, techniques, and procedures (TTPs) using MITRE ATT&CK®
        revolutionized detection and response. Focusing on TTPs creates an opportunity for high-fidelity detection of
        adversaries. If we can detect a behavior, the adversary will need to change behaviors – increasing cost and risk
        for the adversary.
      </p>
      <p>
        Detecting adversary behaviors is challenging. There are often many approaches to implementing a single behavior
        and adversaries commonly use native capabilities (living off the land), making it difficult to differentiate
        adversary activity from normal user activity.
      </p>
      <p>
        Adversary TTPs occur in sequences. Understanding these sequences creates an opportunity to improve detection. If
        we know that <a href="https://attack.mitre.org/techniques/T1566/">Phishing</a> is followed by <a
          href="https://attack.mitre.org/techniques/T1055/">Process Injection</a> and then <a
          href="https://attack.mitre.org/techniques/T1574/">Hijack Execution Flow</a>, we can begin looking for
        this pattern of TTPs. This sounds good in theory, but how does a defender know which behaviors are likely to
        have occurred together?
      </p>
      <p>
        The Technique Inference Engine (TIE) uses a machine learning model trained on cyber threat intelligence to
        recommend likely TTPs based on a known input TTP. TIE will help analysts quickly understand what is likely to
        have happened next based on a broad corpus of threat intelligence.
      </p>
      <p>
        Investigations of adversary intrusions are improved by focusing analysts' time on likely intrusion methods,
        rather than randomness. As new activity is detected, our model can be retrained to account for new or previously
        unseen adversary TTPs.
      </p>
      <p>
        TIE is developed to assist security teams in discovering previously unknown adversary activity based on observed
        adversary activity. The additional context from TIE can be used to:
      </p>
      <ul>
        <li>Prioritize which techniques to look for first during a cyber triage event.</li>
        <li>Improve post-mortem incident analysis by highlighting potential sensing, detection, and reporting gaps.</li>
        <li>Suggest similar or related attack vectors as part of cyber assurance.</li>
        <li>Aid in the creation of Adversary Emulation plans.</li>
      </ul>
      <h1 id="problem-formulation">Problem Formulation</h1>
      <blockquote>
        <b>Problem Statement:</b> Given a list of observed techniques, infer the next most likely techniques.
      </blockquote>
      <p>
        Our choice of problem formulation should allow us to answer the research question at hand given our dataset. We
        analyzed approximately 6,000 Cyber Threat Intelligence (CTI) reports which included roughly 600 ATT&CK
        techniques. Given some subset of the dataset used for training data, we must infer additional techniques which
        may be part of the CTI. We must validate the results based on the reserved test set.
      </p>
      <p>
        A problem immediately arises with this setup. CTI is well known to offer a biased view on the underlying threat
        based on the popularity of techniques in the literature, the expertise of the reporting agency or individual,
        and the detected (or undetected) indicators of compromise (IOC) [1]. In other words, there are two levels of
        bias present in CTI reports, and a third which is introduced in tagging CTI with their relevant ATT&CK
        techniques:
      </p>
      <ol>
        <li>
          Discrepancy between the techniques that occurred vice those that were observed to have occurred.
        </li>
        <li>
          Human-introduced error in translating the observed techniques to a CTI report.
        </li>
        <li>
          A third form of bias is introduced when these reports are later tagged by other analysts with the relevant
          MITRE ATT&CK techniques.
        </li>
      </ol>
      <p>
        On average, each of these biases lead to an underreporting of techniques involved in an incident. Therefore, if
        the model over predicts the techniques present for a particular report, there are two potential reasons.
      </p>
      <ol>
        <li>
          The model erred in its prediction, or
        </li>
        <li>
          The model was correct and identified a technique that was not tagged when
          it should have been.
        </li>
      </ol>
      <p>
        We can assume the more we punish these over-predictions, the less the model will generalize
        to other reports with different analyst-introduced biases.
      </p>
      <p>
        Given these challenges, it seems best to formulate this as an unsupervised learning problem in which we leverage
        the underlying structure of the data to provide inferences as to additional TTPs which may be involved in a
        particular report. We are immediately drawn to unsupervised recommender systems, which allow us to “recommend”
        additional techniques to be part of an entity, or report. This is analogous to the canonical example where a
        system recommends movies to a particular user, something that we should all recognize from any movie streaming
        platform. The model is not necessarily punished for providing a large sequence of recommendations—in fact, a
        movie recommender system makes a recommendation for every movie in its training corpus. Rather, the more
        important aspect is the relative ordering of the recommendations—which is fitting to our problem statement of
        providing the “next most likely techniques.”
      </p>
      <h1 id="model-selection">Model Selection</h1>
      <p>
        The most widely known and used recommender system architecture is the matrix factorization model. The model is
        based on the assumption that there exists some unknown matrix $A$ representing the ratings of each of $M$ items
        by $N$ entities. (In the canonical example, the entities are users and the items are movies.). However, only a
        small subset of the entries of $A$ are observed. The problem becomes to generate a matrix $A^\intercal$ which
        minimizes some norm distance to $A$.
      </p>
      <p>
        There are two lenses through which to view this problem. The first is a simple matrix factorization model in
        which $A$ is factored into low-rank embedding matrices $U$ and $V$ such that $A = UV^\intercal T$. To obtain a
        prediction for any entity and item, one simply takes the dot product of their embeddings. Note the similarity to
        the singular value decomposition (SVD) —if $U$ and $V$ were orthogonal matrices, then scaling them to form
        orthonormal bases by factoring out some sigma would result in the SVD decomposition of $A$. Or, to put it in
        reverse, the SVD of $A$ is a special form of $UV^\intercal T$ in which $U$ and $V$ are orthogonal.
        Regularization may be added to either the matrix factorization or SVD to improve generalization with care taken
        to choose an appropriate loss function and optimizer so the problem converges quickly.
      </p>
      <p>
        Alternatively, one may view the problem in terms of Bayesian Matrix Factorization. Under this model, each entry
        of $A$, $A_{ij}$, is assumed to be normally distributed around the dot product of $U_i$ and $V_j$ with some
        variance specific to each item and entity. The problem becomes to maximize the likelihood of the estimated
        matrix by tuning $U$ and $V$. Regularization appears in tuning the variances of $U$ and $V$.
      </p>
      <h1 id="regularization">Regularization</h1>
      <p>
        A fundamental feature of our dataset is that we don't have negative examples. As previously discussed, the
        absence of a particular technique in a report could be due to either that technique not being present or being
        underreporting. We therefore choose not to assume any negative examples so our training dataset is limited to
        affirmative, “this technique was in that report” entries. In matrix terms, we don't fill in all the sparse
        entries of $A$ with 0's artificially, because likely some of those sparse entries should actually be 1's.
      </p>
      <p>
        How does this affect the model's predictions? Without regularization, a model could achieve 100% accuracy by
        predicting a 1 for every entry (i.e. predicting every technique is present in every report). Why? Because our
        matrix only has positive examples, it is filled with either 1's or NaN's, so the test set is filled with all
        1's!
      </p>
      <p>
        What's the solution? Regularization. Regularization can punish the magnitude of the embeddings (so their dot
        product, and therefore the predicted value, is lower) or punish large entries of the predicted matrix (gravity
        regularization).
      </p>
      <p>
        Both forms of regularization, on average, decrease the value of the predictions, but they also have the
        additional effect of changing the predictions themselves. This can improve the generalizability of the model, as
        aspects of the model which may have overfit to the dataset are made less extreme.
      </p>
      <h1 id="dataset">Dataset</h1>
      <p>
        In the <RouterLink to="/about#problem-formulation">problem formulation</RouterLink> section, we identified a
        recommender model as best-suited to offering most-likely related techniques given an initial set of techniques.
        The training data for this model is organized in to (sub)sets of techniques that correspond to reports and other
        threat intelligence based information sources such as <a href="https://attack.mitre.org/campaigns/">ATT&CK
          Campaigns</a> and <a href="https://attack.mitre.org/resources/adversary-emulation-plans/">Adversary Emulation
          Plans</a>.
      </p>
      <p>
        The trained model produces a matrix with the above subsets as rows, and individual techniques from the data set
        as columns. In each cell, or intersection, the model predicts a value for each technique's association with the
        subset. In this case, the model will only provide prediction values for techniques that exist in the training
        set. It would not be possible to provide a prediction value for techniques not in the training set as there is
        no reference for the model to associate the technique with any others. This would be a challenge with a small
        sample size, however, <b>611 of the 637 techniques (96%)</b> in the latest version of ATT&CK are represented in
        the training data. The <b>total number of reports is 6,236</b>, which are retrieved from a combination of
        sources that include:
      </p>
      <ul>
        <li>
          MITRE’s OpenCTI repository
        </li>
        <li>
          Data contributed from Center Members
        </li>
        <li>
          ATT&CK Campaigns
        </li>
        <li>
          Threat Report ATT&CK Mapper (TRAM) 2.0 annotated CTI reports (subset of 50 ATT&CK techniques)
        </li>
        <li>
          Adversary Emulation Library
        </li>
        <li>
          Attack Flows
        </li>
      </ul>
      <p>
        <b>Overview of TIE Dataset Fields:</b>
      </p>
      <p>
        Each Report in the dataset has the following keys and descriptions:
      </p>
      <ul>
        <li><code>id</code>: integer; unique report identifier.</li>
        <li><code>associated_software</code>: list; software in ATT&CK that are related to the report.</li>
        <li><code>associated_campaigns</code>: list; campaigns in ATT&CK that are related to the report.</li>
        <li><code>associated_groups</code>: list; threat groups in ATT&CK that are related to the report.</li>
        <li><code>origin_of_data</code>: string; the dataset in which the report was derived from.</li>
        <li><code>references</code>: list of dictionaries; any URLs and citation source names for the report.</li>
        <li><code>mitre_techniques</code>: dictionary; ATT&CK Enterprise technique IDs and their associated frequency
          count.</li>
      </ul>
    </div>
  </div>
</template>

<script lang="ts">
// Dependencies
import { defineComponent } from "vue";
// Components
import { RouterLink } from "vue-router";
// Declarations
declare const MathJax: { typeset: () => void }

export default defineComponent({
  name: "AboutView",
  mounted() {
    MathJax.typeset();
  },
  updated() {
    MathJax.typeset();
  },
  components: { RouterLink }
});
</script>

<style lang="scss" scoped>
@use "@/assets/styles/engenuity_scaling_system.scss" as scale;

.about {
  display: flex;
  justify-content: center;
  width: 100%;
  margin: scale.size("xxh") 0em;
}

.about-contents {
  width: 100%;
  max-width: scale.$max-width;
  padding: 0em scale.size("xxh");
}

.about-contents :first-child {
  margin-top: 0em;
}

.about-contents :last-child {
  margin-bottom: 0em;
}

h1,
h2,
h3,
h4,
h5,
h6,
li,
ol,
p {
  margin: scale.size("s") 0em;
}

img {
  display: block;
  width: 100%;
  margin: scale.size("xxl") auto;
}
</style>
