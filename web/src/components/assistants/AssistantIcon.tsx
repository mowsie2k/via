import { Persona } from "@/app/admin/assistants/interfaces";
import React from "react";
import { Tooltip } from "../tooltip/Tooltip";
import { createSVG } from "@/lib/assistantIconUtils";
import { buildImgUrl } from "@/app/chat/files/images/utils";
import vvLogo from "../../../public/vv-logo.png"

export function darkerGenerateColorFromId(id: string): string {
  const hash = Array.from(id).reduce(
    (acc, char) => acc + char.charCodeAt(0),
    0
  );
  const hue = (hash * 137.508) % 360; // Use golden angle approximation
  // const saturation = 40 + (hash % 10); // Saturation between 40-50%
  // const lightness = 40 + (hash % 10); // Lightness between 40-50%
  const saturation = 35 + (hash % 10); // Saturation between 40-50%
  const lightness = 35 + (hash % 10); // Lightness between 40-50%

  return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
}
/*
export function AssistantIcon({
  assistant,
  size,
  border,
}: {
  assistant: Persona;

export function AssistantIcon({
  assistant,
  size,
  border,
}: {
  assistant: Persona;
  size?: "small" | "medium" | "large";
  border?: boolean;
}) {
  return (
    <Tooltip delayDuration={1000} content={assistant.description}>
      <img
        className={`object-cover object-center rounded-sm overflow-hidden transition-opacity duration-300 opacity-100
          ${size === "large" ? "w-8 h-8" : "w-6 h-6"}
          ${border ? "ring ring-[1px] ring-border-strong" : ""}`}
        src={vvLogo}
        alt={assistant.name}
        loading="lazy"
      />
    </Tooltip>
  );
}
*/
