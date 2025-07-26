using System.Collections;
using UnityEngine;
using System.Net.Http;
using System.Threading.Tasks;
using Newtonsoft.Json.Linq;

public class PoseUpdater : MonoBehaviour
{
    public Transform leftShoulder, rightShoulder, leftElbow, rightElbow;
    public Transform leftPec, rightPec, Hips, Neck, Head;
    public Transform leftWrist, rightWrist;

    private HttpClient client = new HttpClient();
    private readonly string apiUrl = "http://localhost:5000/pose";

    // Target rotations and positions for smoothing
    private Quaternion targetLeftShoulderRot, targetRightShoulderRot;
    private Quaternion targetLeftElbowRot, targetRightElbowRot;
    private Quaternion targetLeftWristRot, targetRightWristRot;
    private Quaternion targetHipsRot, targetNeckRot, targetHeadRot;

    private Vector3 targetLeftPecPos, targetRightPecPos;
    private Vector3 targetLeftShoulderPos, targetRightShoulderPos;

    void Start()
    {
        StartCoroutine(UpdatePoseLoop());
    }

    IEnumerator UpdatePoseLoop()
    {
        while (true)
        {
            Debug.Log("Still looping");
            Task<string> getTask = client.GetStringAsync(apiUrl);
            yield return new WaitUntil(() => getTask.IsCompleted);

            if (!getTask.IsFaulted && !getTask.IsCanceled)
            {
                ApplyPose(getTask.Result);
            }
            else
            {
                Debug.LogWarning("Failed to fetch pose data.");
            }

            yield return new WaitForSeconds(0.1f);
        }
    }

    void ApplyPose(string json)
    {
        try
        {
            JObject poseData = JObject.Parse(json);

            SetRotationFromJson(leftShoulder, poseData["leftShoulderRotate"], ref targetLeftShoulderRot);
            SetRotationFromJson(rightShoulder, poseData["rightShoulderRotate"], ref targetRightShoulderRot);
            SetRotationFromJson(leftElbow, poseData["leftElbowRotate"], ref targetLeftElbowRot);
            SetRotationFromJson(rightElbow, poseData["rightElbowRotate"], ref targetRightElbowRot);
            SetRotationFromJson(leftWrist, poseData["leftWrist"], ref targetLeftWristRot);
            SetRotationFromJson(rightWrist, poseData["rightWrist"], ref targetRightWristRot);
            SetRotationFromJson(Hips, poseData["Hips"], ref targetHipsRot);
            SetRotationFromJson(Neck, poseData["Neck"], ref targetNeckRot);
            SetRotationFromJson(Head, poseData["Head"], ref targetHeadRot);

            SetPositionFromJson(leftPec, poseData["leftPecPos"], ref targetLeftPecPos);
            SetPositionFromJson(rightPec, poseData["rightPecPos"], ref targetRightPecPos);
            SetPositionFromJson(leftShoulder, poseData["leftShoulderPos"], ref targetLeftShoulderPos);
            SetPositionFromJson(rightShoulder, poseData["rightShoulderPos"], ref targetRightShoulderPos);

            Debug.Log("Received Pose JSON: " + json);
        }
        catch (System.Exception ex)
        {
            Debug.LogError("Error parsing/applying pose: " + ex.Message);
        }
    }

    void SetRotationFromJson(Transform bone, JToken rotation, ref Quaternion targetRot)
    {
        if (bone == null || rotation == null) return;

        float x = rotation.Value<float>("x");
        float y = rotation.Value<float>("y");
        float z = rotation.Value<float>("z");

        targetRot = Quaternion.Euler(x, y, z);
    }

    void SetPositionFromJson(Transform bone, JToken position, ref Vector3 targetPos)
    {
        if (bone == null || position == null) return;

        float x = position.Value<float>("x");
        float y = position.Value<float>("y");
        float z = position.Value<float>("z");

        targetPos = new Vector3(x, y, z);
    }

    void Update()
    {
        float smoothing = 5f * Time.deltaTime;

        if (leftShoulder)
        {
            leftShoulder.localRotation = Quaternion.Slerp(leftShoulder.localRotation, targetLeftShoulderRot, smoothing);
            leftShoulder.localPosition = Vector3.Lerp(leftShoulder.localPosition, targetLeftShoulderPos, smoothing);
        }

        if (rightShoulder)
        {
            rightShoulder.localRotation = Quaternion.Slerp(rightShoulder.localRotation, targetRightShoulderRot, smoothing);
            rightShoulder.localPosition = Vector3.Lerp(rightShoulder.localPosition, targetRightShoulderPos, smoothing);
        }

        if (leftElbow) leftElbow.localRotation = Quaternion.Slerp(leftElbow.localRotation, targetLeftElbowRot, smoothing);
        if (rightElbow) rightElbow.localRotation = Quaternion.Slerp(rightElbow.localRotation, targetRightElbowRot, smoothing);
        if (leftWrist) leftWrist.localRotation = Quaternion.Slerp(leftWrist.localRotation, targetLeftWristRot, smoothing);
        if (rightWrist) rightWrist.localRotation = Quaternion.Slerp(rightWrist.localRotation, targetRightWristRot, smoothing);
        if (Hips) Hips.localRotation = Quaternion.Slerp(Hips.localRotation, targetHipsRot, smoothing);
        if (Neck) Neck.localRotation = Quaternion.Slerp(Neck.localRotation, targetNeckRot, smoothing);
        if (Head) Head.localRotation = Quaternion.Slerp(Head.localRotation, targetHeadRot, smoothing);

        if (leftPec) leftPec.localPosition = Vector3.Lerp(leftPec.localPosition, targetLeftPecPos, smoothing);
        if (rightPec) rightPec.localPosition = Vector3.Lerp(rightPec.localPosition, targetRightPecPos, smoothing);
    }

    private void OnDestroy()
    {
        client.Dispose();
    }
}
