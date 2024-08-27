"use client";
import { User } from "@/lib/types";
import { UserDropdown } from "../UserDropdown";
import { FiShare2 } from "react-icons/fi";
import { SetStateAction, useContext, useEffect } from "react";
import { NewChatIcon } from "../icons/icons";
import { NEXT_PUBLIC_NEW_CHAT_DIRECTS_TO_SAME_PERSONA } from "@/lib/constants";
import { ChatSession } from "@/app/chat/interfaces";
import Link from "next/link";
import { SettingsContext } from "../settings/SettingsProvider";
import { pageType } from "@/app/chat/sessionSidebar/types";
import { useRouter } from "next/navigation";
import { ChatBanner } from "@/app/chat/ChatBanner";
import LogoType from "../header/LogoType";

export default function FunctionalHeader({
  user,
  page,
  currentChatSession,
  setSharingModalVisible,
  toggleSidebar = () => null,
  reset = () => null,
  sidebarToggled,
}: {
  reset?: () => void;
  page: pageType;
  user: User | null;
  sidebarToggled?: boolean;
  currentChatSession?: ChatSession | null | undefined;
  setSharingModalVisible?: (value: SetStateAction<boolean>) => void;
  toggleSidebar?: () => void;
}) {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.metaKey || event.ctrlKey) {
        switch (event.key.toLowerCase()) {
          case "u":
            event.preventDefault();
            window.open(
              `/${page}` +
                (NEXT_PUBLIC_NEW_CHAT_DIRECTS_TO_SAME_PERSONA &&
                currentChatSession
                  ? `?assistantId=${currentChatSession.persona_id}`
                  : ""),
              "_self"
            );
            break;
        }
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, []);
  const router = useRouter();

  const handleNewChat = () => {
    reset();
    const newChatUrl =
      `/${page}` +
      (NEXT_PUBLIC_NEW_CHAT_DIRECTS_TO_SAME_PERSONA && currentChatSession
        ? `?assistantId=${currentChatSession.persona_id}`
        : "");
    router.push(newChatUrl);
  };
  return (
    <div className="pb-6 left-0 sticky top-0 z-20 w-full relative flex">
      <div className="mt-2 mx-4 text-text-700 flex w-full">
        <div className="absolute  z-[100] my-auto flex items-center text-xl font-bold">
          <button
            onClick={() => toggleSidebar()}
            className="pt-[2px] desktop:invisible mb-auto"
          >
            <FiSidebar size={20} />
          </button>
          <div className="invisible break-words inline-block w-fit ml-2 text-text-700 text-xl">
            <div className="max-w-[200px]">
              {enterpriseSettings && enterpriseSettings.application_name ? (
                <div>
                  <HeaderTitle>
                    {enterpriseSettings.application_name}
                  </HeaderTitle>
                  {!NEXT_PUBLIC_DO_NOT_USE_TOGGLE_OFF_DANSWER_POWERED && (
                    <p className="text-xs text-subtle">Powered by Danswer</p>
                  )}
                </div>
              ) : (
                <HeaderTitle>VIA</HeaderTitle>
              )}
            </div>
          </div>

          {page == "chat" && (
            <Tooltip delayDuration={1000} content={`${commandSymbol}U`}>
              <Link
                className="mobile:hidden my-auto"
                href={
                  `/${page}` +
                  (NEXT_PUBLIC_NEW_CHAT_DIRECTS_TO_SAME_PERSONA &&
                  currentChatSession
                    ? `?assistantId=${currentChatSession.persona_id}`
                    : "")
                }
              >
                <div className="cursor-pointer ml-2 flex-none text-text-700 hover:text-text-600 transition-colors duration-300">
                  <NewChatIcon size={20} />
                </div>
              </Link>
            </Tooltip>
          )}
        </div>

        <div className="invisible">
          <LogoType
            page={page}
            toggleSidebar={toggleSidebar}
            handleNewChat={handleNewChat}
          />
        </div>

        <div className="absolute right-0 top-0 flex gap-x-2">
          {setSharingModalVisible && (
            <div
              onClick={() => setSharingModalVisible(true)}
              className="mobile:hidden my-auto rounded cursor-pointer hover:bg-hover-light"
            >
              <FiShare2 size="18" />
            </div>
          )}

          <div className="mobile:hidden flex my-auto">
            <UserDropdown user={user} />
          </div>
          <Link
            className="desktop:hidden my-auto"
            href={
              `/${page}` +
              (NEXT_PUBLIC_NEW_CHAT_DIRECTS_TO_SAME_PERSONA &&
              currentChatSession
                ? `?assistantId=${currentChatSession.persona_id}`
                : "")
            }
          >
            <div className="cursor-pointer mr-4 flex-none text-text-700 hover:text-text-600 transition-colors duration-300">
              <NewChatIcon size={20} />
            </div>
          </Link>
        </div>
      </div>

      {page != "assistants" && (
        <div className="h-24 left-0 absolute top-0 z-10 w-full bg-gradient-to-b via-50% z-[-1] from-background via-background to-background/10 flex" />
      )}
    </div>
  );
}
