import { View } from "@react-pdf/renderer";
import {
  ResumePDFSection,
  ResumePDFText,
} from "components/Resume/ResumePDF/common";
import { styles, spacing } from "components/Resume/ResumePDF/styles";
import type { ResumeSkills } from "lib/redux/types";

export const ResumePDFSkills = ({
  heading,
  skills,
  themeColor,
}: {
  heading: string;
  skills: ResumeSkills;
  themeColor: string;
  showBulletPoints?: boolean;
}) => {
  const { descriptions } = skills;

  return (
    <ResumePDFSection themeColor={themeColor} heading={heading}>
      <View style={{ ...styles.flexCol, marginTop: spacing["0.5"] }}>
        {descriptions.map((desc, idx) => (
          <ResumePDFText key={idx} style={{ marginTop: 0 }}>
            {desc}
          </ResumePDFText>
        ))}
      </View>
    </ResumePDFSection>
  );
};
