"use client";

import React from "react";
import { FiExternalLink, FiCheckCircle, FiMessageSquare } from "react-icons/fi";
import type { ResourceCard as ResourceCardType } from "../types/ai";

interface ResourceCardProps {
  resource: ResourceCardType;
}

const ResourceCard: React.FC<ResourceCardProps> = ({ resource }) => {
  if (resource.type === "youtube") {
    return (
      <a
        href={resource.url}
        target="_blank"
        rel="noopener noreferrer"
        style={{
          display: "flex",
          flexDirection: "column",
          width: "240px",
          flexShrink: 0,
          borderRadius: "8px",
          overflow: "hidden",
          border: "1px solid var(--border)",
          background: "var(--panel-content-bg)",
          textDecoration: "none",
          transition: "transform 0.15s ease, box-shadow 0.15s ease",
          cursor: "pointer",
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = "translateY(-2px)";
          e.currentTarget.style.boxShadow = "0 4px 12px rgba(0,0,0,0.15)";
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = "translateY(0)";
          e.currentTarget.style.boxShadow = "none";
        }}
      >
        {resource.thumbnailUrl && (
          <div style={{ position: "relative", paddingTop: "56.25%", background: "#000" }}>
            <img
              src={resource.thumbnailUrl}
              alt={resource.title}
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                width: "100%",
                height: "100%",
                objectFit: "cover",
              }}
            />
            <div
              style={{
                position: "absolute",
                top: "8px",
                right: "8px",
                background: "rgba(0,0,0,0.8)",
                padding: "4px 8px",
                borderRadius: "4px",
                fontSize: "10px",
                fontWeight: 600,
                color: "#fff",
              }}
            >
              YouTube
            </div>
          </div>
        )}
        <div style={{ padding: "10px 12px", display: "flex", flexDirection: "column", gap: "6px" }}>
          <div
            style={{
              fontSize: "13px",
              fontWeight: 600,
              color: "var(--text)",
              lineHeight: "1.4",
              display: "-webkit-box",
              WebkitLineClamp: 2,
              WebkitBoxOrient: "vertical",
              overflow: "hidden",
            }}
          >
            {resource.title}
          </div>
          <div
            style={{
              fontSize: "11px",
              color: "var(--panel-text)",
              opacity: 0.7,
            }}
          >
            {resource.channel}
          </div>
          {resource.description && (
            <div
              style={{
                fontSize: "11px",
                color: "var(--panel-text)",
                opacity: 0.6,
                lineHeight: "1.4",
                display: "-webkit-box",
                WebkitLineClamp: 2,
                WebkitBoxOrient: "vertical",
                overflow: "hidden",
              }}
            >
              {resource.description}
            </div>
          )}
          <div style={{ display: "flex", alignItems: "center", gap: "4px", marginTop: "4px" }}>
            <FiExternalLink size={11} style={{ color: "var(--accent)", opacity: 0.7 }} />
            <span style={{ fontSize: "10px", color: "var(--accent)", opacity: 0.7 }}>Watch on YouTube</span>
          </div>
        </div>
      </a>
    );
  }

  if (resource.type === "stackoverflow") {
    return (
      <a
        href={resource.url}
        target="_blank"
        rel="noopener noreferrer"
        style={{
          display: "flex",
          flexDirection: "column",
          width: "280px",
          flexShrink: 0,
          borderRadius: "8px",
          border: "1px solid var(--border)",
          background: "var(--panel-content-bg)",
          padding: "12px",
          textDecoration: "none",
          transition: "transform 0.15s ease, box-shadow 0.15s ease",
          cursor: "pointer",
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = "translateY(-2px)";
          e.currentTarget.style.boxShadow = "0 4px 12px rgba(0,0,0,0.15)";
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = "translateY(0)";
          e.currentTarget.style.boxShadow = "none";
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "8px" }}>
          <div
            style={{
              fontSize: "10px",
              fontWeight: 600,
              color: "#F48024",
              background: "rgba(244, 128, 36, 0.1)",
              padding: "2px 6px",
              borderRadius: "3px",
            }}
          >
            Stack Overflow
          </div>
          {resource.isAnswered && (
            <div style={{ display: "flex", alignItems: "center", gap: "3px" }}>
              <FiCheckCircle size={10} style={{ color: "#5cb85c" }} />
              <span style={{ fontSize: "10px", color: "#5cb85c", fontWeight: 500 }}>Answered</span>
            </div>
          )}
        </div>

        <div
          style={{
            fontSize: "13px",
            fontWeight: 600,
            color: "var(--text)",
            lineHeight: "1.4",
            marginBottom: "8px",
            display: "-webkit-box",
            WebkitLineClamp: 3,
            WebkitBoxOrient: "vertical",
            overflow: "hidden",
          }}
        >
          {resource.title}
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "8px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
            <span style={{ fontSize: "11px", color: "var(--panel-text)", opacity: 0.7 }}>Score:</span>
            <span style={{ fontSize: "11px", fontWeight: 600, color: "var(--text)" }}>{resource.score}</span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
            <FiMessageSquare size={11} style={{ color: "var(--panel-text)", opacity: 0.7 }} />
            <span style={{ fontSize: "11px", color: "var(--panel-text)", opacity: 0.7 }}>
              {resource.answerCount} {resource.answerCount === 1 ? "answer" : "answers"}
            </span>
          </div>
        </div>

        {resource.tags && resource.tags.length > 0 && (
          <div style={{ display: "flex", flexWrap: "wrap", gap: "4px", marginBottom: "8px" }}>
            {resource.tags.map((tag, i) => (
              <span
                key={i}
                style={{
                  fontSize: "10px",
                  color: "var(--accent)",
                  background: "var(--subtle-bg)",
                  padding: "2px 6px",
                  borderRadius: "3px",
                  border: "1px solid var(--border)",
                }}
              >
                {tag}
              </span>
            ))}
          </div>
        )}

        <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
          <FiExternalLink size={11} style={{ color: "var(--accent)", opacity: 0.7 }} />
          <span style={{ fontSize: "10px", color: "var(--accent)", opacity: 0.7 }}>View on Stack Overflow</span>
        </div>
      </a>
    );
  }

  if (resource.type === "python_docs") {
    return (
      <a
        href={resource.url}
        target="_blank"
        rel="noopener noreferrer"
        style={{
          display: "flex",
          flexDirection: "column",
          width: "280px",
          flexShrink: 0,
          borderRadius: "8px",
          border: "1px solid var(--border)",
          background: "var(--panel-content-bg)",
          padding: "12px",
          textDecoration: "none",
          transition: "transform 0.15s ease, box-shadow 0.15s ease",
          cursor: "pointer",
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = "translateY(-2px)";
          e.currentTarget.style.boxShadow = "0 4px 12px rgba(0,0,0,0.15)";
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = "translateY(0)";
          e.currentTarget.style.boxShadow = "none";
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "8px" }}>
          <div
            style={{
              fontSize: "10px",
              fontWeight: 600,
              color: "#3776ab",
              background: "rgba(55, 118, 171, 0.1)",
              padding: "2px 6px",
              borderRadius: "3px",
            }}
          >
            Python Docs
          </div>
        </div>

        <div
          style={{
            fontSize: "13px",
            fontWeight: 600,
            color: "var(--text)",
            lineHeight: "1.4",
            marginBottom: "8px",
            display: "-webkit-box",
            WebkitLineClamp: 3,
            WebkitBoxOrient: "vertical",
            overflow: "hidden",
          }}
        >
          {resource.title}
        </div>

        {resource.snippet && (
          <div
            style={{
              fontSize: "11px",
              color: "var(--panel-text)",
              opacity: 0.7,
              lineHeight: "1.4",
              marginBottom: "8px",
              display: "-webkit-box",
              WebkitLineClamp: 3,
              WebkitBoxOrient: "vertical",
              overflow: "hidden",
            }}
          >
            {resource.snippet}
          </div>
        )}

        <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
          <FiExternalLink size={11} style={{ color: "var(--accent)", opacity: 0.7 }} />
          <span style={{ fontSize: "10px", color: "var(--accent)", opacity: 0.7 }}>View on Python.org</span>
        </div>
      </a>
    );
  }

  return null;
};

export default ResourceCard;
